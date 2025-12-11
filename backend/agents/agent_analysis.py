import logging
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class AgentAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute_analysis_task(self, task, data: pd.DataFrame) -> dict:
        analysis_type = task.get('type')
        self.logger.info(f"AgentAnalysis: Executing analysis task of type '{analysis_type}'")

        if analysis_type == 'calculate_total_downtime':
            if data.empty:
                return {
                    "total_downtime_minutes": 0,
                    "entry_count": 0,
                    "top_downtimes": []
                }
            data['Downtime Minutes'] = pd.to_numeric(data['Downtime Minutes'], errors='coerce').fillna(0)
            top_incidents_df = data.nlargest(5, 'Downtime Minutes')

            total_downtime = data['Downtime Minutes'].sum()
            entry_count = len(data)
            top_incidents = top_incidents_df.rename(columns={
                'Downtime Minutes': 'minutes',
                'documents': 'note',
                'Line': 'line',
                'Timestamp': 'timestamp'
            })
            top_incidents['note'] = top_incidents['note'].apply(lambda x: x if x else "No notes provided")
            top_incidents['minutes'] = top_incidents['minutes'].astype(int)
            top_incidents = top_incidents[['minutes', 'note', 'line', 'timestamp']].to_dict('records')

            return {
                "total_downtime_minutes": int(total_downtime),
                "entry_count": int(entry_count),
                "top_downtimes": top_incidents
            }

        elif analysis_type == 'aggregate_by_line':
            if data.empty:
                return {"top_lines_by_downtime": []}

            data['Downtime Minutes'] = pd.to_numeric(data['Downtime Minutes'], errors='coerce').fillna(0)
            line_downtime = data.groupby('Line')['Downtime Minutes'].sum().sort_values(ascending=False).head(5)
            top_lines_formatted = line_downtime.reset_index().rename(
                columns={'Line': 'line', 'Downtime Minutes': 'total_downtime_minutes'}
            ).to_dict('records')

            return {"top_lines_by_downtime": top_lines_formatted}

        elif analysis_type == 'cluster_and_aggregate':
            self.logger.info("🔬 [Analysis] Clustering notes to find top causes...")

            if 'embeddings' not in data.columns:
                return {"error": "Embeddings not found in data, cannot perform clustering."}

            logs_with_notes = data[data['documents'].notna() & (data['documents'] != '') & data['embeddings'].notna()].copy()
            if logs_with_notes.empty:
                return {"error": "No notes with embeddings were found to analyze."}

            embeddings = np.array(logs_with_notes['embeddings'].tolist())
            n_samples, n_features = embeddings.shape

            n_components = min(n_samples, n_features, 20)
            if n_components < 1:
                return {"error": "Not enough data to perform PCA."}

            pca = PCA(n_components=n_components, random_state=42)
            reduced_embeddings = pca.fit_transform(embeddings)

            n_clusters = 5
            if n_samples < n_clusters:
                n_clusters = n_samples

            if n_clusters < 1:
                return {"error": "Not enough data to perform clustering."}

            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            logs_with_notes['cluster'] = kmeans.fit_predict(reduced_embeddings)

            logs_with_notes['Downtime Minutes'] = pd.to_numeric(logs_with_notes['Downtime Minutes'], errors='coerce').fillna(0)

            def get_most_frequent(series):
                return series.mode()[0] if not series.empty else "N/A"

            cluster_analysis = logs_with_notes.groupby('cluster').agg(
                cluster_label=('documents', get_most_frequent),
                total_downtime_minutes=('Downtime Minutes', 'sum'),
                incident_count=('documents', 'size')
            )

            ranked_clusters_df = cluster_analysis.sort_values('total_downtime_minutes', ascending=False)

            return {"top_causes": ranked_clusters_df.reset_index(drop=True).to_dict('records')}

        elif analysis_type == 'find_most_frequent_causes':
            if data.empty:
                return {"most_frequent_downtimes": []}

            filtered_data = data[data['documents'].notna() & (data['documents'] != '')].copy()

            if filtered_data.empty:
                return {"error": "No notes were found to analyze."}

            total_logs_with_notes = len(filtered_data)
            note_counts = filtered_data['documents'].value_counts().head(5)

            most_frequent_downtimes = []
            for note, count in note_counts.items():
                most_frequent_downtimes.append({
                    "note": note,
                    "incident_count": int(count),
                    "percentage": round((count / total_logs_with_notes) * 100, 1)
                })

            return {
                "total_logs_analyzed": total_logs_with_notes,
                "most_frequent_downtimes": most_frequent_downtimes
            }

        else:
            self.logger.info("Analysis: Formatting 'passthrough' data for synthesizer...")

            if data.empty:
                return {}

            is_known_issue = 'solution' in data.columns

            if is_known_issue:
                incidents_df = data[['title', 'description', 'solution', 'author']].copy()
                incidents = incidents_df.head(3).to_dict('records') # Take top 3 as per original
            else:
                incidents_df = data.copy()
                incidents_df['Downtime Minutes'] = pd.to_numeric(incidents_df['Downtime Minutes'], errors='coerce').fillna(0)
                incidents_df['documents'] = incidents_df['documents'].fillna("No notes provided") # Fill empty notes

                incidents_df = incidents_df.rename(columns={
                    'Downtime Minutes': 'minutes',
                    'Notes': 'note',
                    'Line': 'line',
                    'Timestamp': 'timestamp'
                })

                incidents = incidents_df.sort_values(by='minutes', ascending=False).head(10)[
                    ['minutes', 'note', 'line', 'timestamp']
                ].to_dict('records')

            result_data = {
                "entry_count": len(data),
                "display_incidents": incidents
            }

            if is_known_issue:
                return {"known_issue_results": result_data}
            else:
                return {"downtime_log_results": result_data}
