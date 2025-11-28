import { X } from 'lucide-react';
import './AboutModal.css';

export default function AboutModal({ isOpen, onClose }) {

    const formatDate = (dateString) => {
        if (!dateString || dateString.includes('...')) return dateString;
        try {
            return new Date(dateString).toLocaleString();
        } catch (e) {
            return 'Invalid Date';
        }
    };

    if (!isOpen) {
        return null;
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <h2 className="modal-title">About this Application</h2>
                    <button onClick={onClose} className="modal-close-button">
                        <X className="close-icon" />
                    </button>
                </div>

                {/* Body */}
                <div className="modal-body">
                    <div className="version-grid">

                        {/* Frontend Info */}
                        <div className="version-section">
                            <h3 className="section-title">Frontend</h3>
                            <div className="info-list">
                                <div className="info-item">
                                    <span className="info-label">Version:</span>
                                    <span className="info-value">{frontend.appVersion}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Environment:</span>
                                    <span className="info-value environment-badge">{frontend.environment}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Build ID:</span>
                                    <code className="info-code">{frontend.commitHash}</code>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Build Date:</span>
                                    <span className="info-value">{formatDate(frontend.buildDate)}</span>
                                </div>
                            </div>
                        </div>

                        {/* Backend Info */}
                        <div className="version-section">
                            <h3 className="section-title">Backend (API)</h3>
                            <div className="info-list">
                                <div className="info-item">
                                    <span className="info-label">Version:</span>
                                    <span className="info-value">{backend.app_version}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Environment:</span>
                                    <span className="info-value environment-badge">{backend.environment}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Build ID:</span>
                                    <code className="info-code">{backend.commit_hash}</code>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Build Date:</span>
                                    <span className="info-value">{formatDate(backend.build_date)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="modal-footer">
                    <button onClick={onClose} className="modal-close-button-primary">
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
