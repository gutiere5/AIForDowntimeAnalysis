import { useState, useEffect } from 'react';
import { X, Plus, Edit2, Trash2, Save, AlertCircle, Search } from 'lucide-react';
import api from '@/assets/api';
import './KnownIssuesModal.css';

export default function KnownIssuesModal({ isOpen, onClose }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingIssue, setEditingIssue] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    solution: '',
    author: ''
  });
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchKnownIssues();
    }
  }, [isOpen]);

  const fetchKnownIssues = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getKnownIssues();
      setIssues(data);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch known issues:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setIsAddingNew(true);
    setEditingIssue(null);
    setFormData({ title: '', description: '', solution: '', author: '' });
  };

  const handleEdit = (issue) => {
    setIsAddingNew(false);
    setEditingIssue(issue.id);
    setFormData({
      title: issue.title,
      description: issue.description,
      solution: issue.solution,
      author: issue.author
    });
  };

  const handleCancel = () => {
    setIsAddingNew(false);
    setEditingIssue(null);
    setFormData({ description: '', symptoms: '', solution: '' });
  };

  const handleSave = async () => {
    setError(null);
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }
    if (!formData.description.trim()) {
      setError('Description is required');
      return;
    }
    if (!formData.solution.trim()) {
      setError('Solution is required');
      return;
    }
    if (!formData.author.trim()) {
      setError('Author is required');
      return;
    }

    try {
      if (isAddingNew) {
        const newIssue = await api.addKnownIssue(formData);
        setIssues([...issues, newIssue]);
      } else if (editingIssue) {
        await api.updateKnownIssue(editingIssue, formData);
        setIssues(issues.map(issue =>
          issue.id === editingIssue ? { ...issue, ...formData } : issue
        ));
      }
      handleCancel();
    } catch (err) {
      setError(err.message);
      console.error('Failed to save known issue:', err);
    }
  };

  const handleDelete = async (issueId) => {
    if (!confirm('Are you sure you want to delete this known issue?')) {
      return;
    }

    setError(null);
    try {
      await api.deleteKnownIssue(issueId);
      setIssues(issues.filter(issue => issue.id !== issueId));
      if (editingIssue === issueId) {
        handleCancel();
      }
    } catch (err) {
      setError(err.message);
      console.error('Failed to delete known issue:', err);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const filteredIssues = issues.filter(issue =>
    issue.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container known-issues-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">Manage Known Issues</h2>
          <button onClick={onClose} className="modal-close-button">
            <X className="close-icon" />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {error && (
            <div className="error-banner">
              <AlertCircle className="error-icon" />
              <span>{error}</span>
            </div>
          )}

          {/* Add New Button */}
          {!isAddingNew && !editingIssue && (
            <button onClick={handleAdd} className="add-issue-button">
              <Plus className="button-icon" />
              <span>Add New Issue</span>
            </button>
          )}

          {/* Add/Edit Form */}
          {(isAddingNew || editingIssue) && (
            <div className="issue-form">
              <h3 className="form-title">
                {isAddingNew ? 'Add New Issue' : 'Edit Issue'}
              </h3>
              <div className="form-group">
                <label className="form-label">Title <span className="required">*</span></label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Brief title of the issue"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Description <span className="required">*</span></label>
                <textarea
                  className="form-textarea"
                  placeholder="Detailed description of the issue"
                  rows={3}
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Solution <span className="required">*</span></label>
                <textarea
                  className="form-textarea"
                  placeholder="How to resolve this issue"
                  rows={3}
                  value={formData.solution}
                  onChange={(e) => handleInputChange('solution', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Author <span className="required">*</span></label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Author of the issue"
                  value={formData.author}
                  onChange={(e) => handleInputChange('author', e.target.value)}
                />
              </div>
              <div className="form-actions">
                <button onClick={handleCancel} className="form-button cancel">
                  Cancel
                </button>
                <button onClick={handleSave} className="form-button save">
                  <Save className="button-icon" />
                  <span>Save</span>
                </button>
              </div>
            </div>
          )}

          {/* Search Bar */}
          {!isAddingNew && !editingIssue && issues.length > 0 && (
            <div className="search-bar">
              <Search className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Search issues by title..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="clear-search-button"
                  title="Clear search"
                >
                  <X className="clear-icon" />
                </button>
              )}
            </div>
          )}

          <div className="issues-list">
            {loading ? (
              <div className="loading-state">Loading known issues...</div>
            ) : filteredIssues.length === 0 && searchQuery ? (
              <div className="empty-state">
                <AlertCircle className="empty-icon" />
                <p>No issues match your search</p>
                <p className="empty-subtitle">Try a different search term</p>
              </div>
            ) : filteredIssues.length === 0 ? (
              <div className="empty-state">
                <AlertCircle className="empty-icon" />
                <p>No known issues found</p>
                <p className="empty-subtitle">Add your first issue to get started</p>
              </div>
            ) : (
              filteredIssues.map((issue) => (
                <div
                  key={issue.id}
                  className={`issue-card ${editingIssue === issue.id ? 'editing' : ''}`}
                >
                  <div className="issue-header">
                    <h4 className="issue-title">{issue.title}</h4>
                    {editingIssue !== issue.id && (
                      <div className="issue-actions">
                        <button
                          onClick={() => handleEdit(issue)}
                          className="action-button edit"
                          title="Edit"
                        >
                          <Edit2 className="action-icon" />
                        </button>
                        <button
                          onClick={() => handleDelete(issue.id)}
                          className="action-button delete"
                          title="Delete"
                        >
                          <Trash2 className="action-icon" />
                        </button>
                      </div>
                    )}
                  </div>
                  <div className="issue-content">
                    <div className="issue-section">
                      <span className="section-label">Description:</span>
                      <p className="section-text">{issue.description}</p>
                    </div>
                    <div className="issue-section">
                      <span className="section-label">Solution:</span>
                      <p className="section-text">{issue.solution}</p>
                    </div>
                    <div className="issue-section">
                      <span className="section-label">Author:</span>
                      <p className="section-text">{issue.author}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
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