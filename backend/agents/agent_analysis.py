import logging
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class AgentAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute_analysis_task(self, task, data):
        analysis_type = task.get('type')
        self.logger.info(f"AgentAnalysis: Executing analysis task of type '{analysis_type}'")

        if analysis_type == 'calculate_total_downtime':
            total_downtime = 0
            incidents = []

            for i in range(len(data['ids'])):
                minutes = float(data['metadatas'][i]['Downtime Minutes'])
                note = data['documents'][i] if data['documents'][i] else "No notes provided"
                line = data['metadatas'][i]['Line']
                timestamp = data['metadatas'][i]['Timestamp']

                total_downtime += minutes
                incidents.append({"minutes": minutes, "note": note, "line": line, "timestamp": timestamp})

            top_incidents = sorted(incidents, key=lambda x: x['minutes'], reverse=True)[:5]

            return {
                "total_downtime_minutes": total_downtime,
                "entry_count": len(data['ids']),
                "top_downtimes": top_incidents
            }

        elif analysis_type == 'aggregate_by_line':
            line_downtime = {}

            for i in range(len(data['ids'])):
                line = data['metadatas'][i]['Line']
                minutes = float(data['metadatas'][i]['Downtime Minutes'])

                if line not in line_downtime:
                    line_downtime[line] = 0.0

                line_downtime[line] += minutes

            sorted_lines = sorted(line_downtime.items(), key=lambda item: item[1], reverse=True)

            top_lines_formatted = []
            for line, total_minutes in sorted_lines[:5]:
                top_lines_formatted.append({
                    "line": line,
                    "total_downtime_minutes": total_minutes
                })
            return {"top_lines_by_downtime": top_lines_formatted}

        elif analysis_type == 'cluster_and_aggregate':
            self.logger.info("🔬 [Analysis] Clustering notes to find top causes...")

            logs_with_notes = []
            for i in range(len(data['ids'])):
                if data['documents'][i]:
                    logs_with_notes.append({
                        "embedding": data['embeddings'][i],
                        "metadata": data['metadatas'][i],
                        "document": data['documents'][i]
                    })

            if not logs_with_notes:
                return {"error": "No notes were found to analyze."}

            embeddings = np.array([log['embedding'] for log in logs_with_notes])

            # Determine the number of components for PCA dynamically
            n_samples, n_features = embeddings.shape
            n_components = min(n_samples, n_features, 20)

            # Ensure n_components is at least 1
            if n_components == 0:
                return {"error": "Not enough data to perform analysis."}

            pca = PCA(n_components=n_components, random_state=42)
            reduced_embeddings = pca.fit_transform(embeddings)

            n_clusters = 5
            if len(logs_with_notes) < n_clusters:
                n_clusters = len(logs_with_notes)

            # Ensure n_clusters is not greater than n_samples
            if n_clusters > n_samples:
                n_clusters = n_samples
            
            # Ensure n_clusters is at least 1
            if n_clusters == 0:
                return {"error": "Not enough data to perform clustering."}


            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(reduced_embeddings)

            cluster_analysis = {}
            for i, log in enumerate(logs_with_notes):
                cluster_id = clusters[i]
                if cluster_id not in cluster_analysis:
                    cluster_analysis[cluster_id] = {
                        "total_downtime": 0,
                        "incident_count": 0,
                        "notes": []
                    }

                cluster_analysis[cluster_id]["total_downtime"] += float(log['metadata']['Downtime Minutes'])
                cluster_analysis[cluster_id]["incident_count"] += 1
                cluster_analysis[cluster_id]["notes"].append(log['document'])

            ranked_clusters = []
            for cluster_id, analysis in cluster_analysis.items():
                label = max(set(analysis['notes']), key=analysis['notes'].count)

                ranked_clusters.append({
                    "cluster_label": label,
                    "total_downtime_minutes": analysis['total_downtime'],
                    "incident_count": analysis['incident_count']
                })

            ranked_clusters = sorted(ranked_clusters, key=lambda x: x['total_downtime_minutes'], reverse=True)
            return {"top_causes": ranked_clusters}

        elif analysis_type == 'find_most_frequent_causes':
            note_counts = {}
            total_logs_with_notes = 0

            for i in range(len(data['ids'])):
                note = data['documents'][i]
                if note:
                    total_logs_with_notes += 1
                    note_counts[note] = note_counts.get(note, 0) + 1

            if not note_counts:
                return {"error": "No notes were found to analyze."}

            sorted_notes = sorted(note_counts.items(), key=lambda item: item[1], reverse=True)

            top_5_notes = []
            for note, count in sorted_notes[:5]:
                top_5_notes.append({
                    "note": note,
                    "incident_count": count,
                    "percentage": round((count / total_logs_with_notes) * 100, 1)
                })

            return {
                "total_logs_analyzed": total_logs_with_notes,
                "most_frequent_downtimes": top_5_notes
            }

        else:
            # This will handle the queries like "Show me all events"
            self.logger.info("Analysis: Formatting 'passthrough' data for synthesizer...")
            ids = data['ids']
            documents = data['documents']
            metadatas = data['metadatas']

            if ids and isinstance(ids[0], list):
                ids = ids[0]
                documents = documents[0]
                metadatas = metadatas[0]

            incidents = []
            entry_count = len(ids)

            for i in range(entry_count):
                incidents.append({
                    "minutes": float(metadatas[i]['Downtime Minutes']),
                    "note": documents[i] if documents[i] else "No notes provided",
                    "line": metadatas[i]['Line'],
                    "timestamp": metadatas[i]['Timestamp']
                })

            top_incidents = sorted(incidents, key=lambda x: x['minutes'], reverse=True)[:10]
            return {
                "entry_count": entry_count,
                "display_incidents": top_incidents
            }
