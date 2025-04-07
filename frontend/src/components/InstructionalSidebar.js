import React from 'react';
import './InstructionalSidebar.css';

// Example content structure - we'll need to pass the actual content dynamically
const defaultContent = {
    title: "Welcome!",
    text: "Select a metric or load a scenario to begin."
};

function InstructionalSidebar({ content = defaultContent }) {
    // In a real implementation, 'content' would likely be determined by the 
    // active state in the main App component (e.g., which form is visible, 
    // what results are displayed).
    
    return (
        <aside className="instructional-sidebar">
            <h4>{content.title}</h4>
            <div className="sidebar-content">
                {/* Render text, potentially with paragraphs or lists */} 
                {typeof content.text === 'string' ? <p>{content.text}</p> : content.text}
                
                {/* Optional: Example Values Section */} 
                {content.examples && (
                     <div className="sidebar-examples">
                         <h5>Examples:</h5>
                         {/* Render examples, maybe as preformatted code or list */} 
                         <pre>{JSON.stringify(content.examples, null, 2)}</pre>
                     </div>
                 )}
                 
                 {/* Optional: Explanation Section */} 
                 {content.explanation && (
                     <div className="sidebar-explanation">
                         <h5>How it Works:</h5>
                         {/* Render explanation */} 
                         <p>{content.explanation}</p>
                     </div>
                 )}
            </div>
        </aside>
    );
}

export default InstructionalSidebar; 