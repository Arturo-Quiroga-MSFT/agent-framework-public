use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;

/// Initialize Python interpreter and set up the environment
pub fn initialize_python() -> PyResult<()> {
    Python::with_gil(|py| {
        // Add parent directory to Python path to find dba_assistant.py
        let sys = py.import("sys")?;
        let path = sys.getattr("path")?;
        
        // Get the path to the parent directory (where dba_assistant.py lives)
        let mut parent_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        parent_dir.pop(); // Remove "src-tauri"
        parent_dir.pop(); // Remove "UI"
        
        path.call_method1("append", (parent_dir.to_str().unwrap(),))?;
        
        Ok(())
    })
}

/// Run a DBA query using the Python agent
pub fn run_python_query(query: String) -> PyResult<String> {
    Python::with_gil(|py| {
        // Import the dba_assistant module
        let dba_module = py.import("dba_assistant")?;
        
        // TODO: Call the appropriate function from dba_assistant.py
        // This is a placeholder - actual implementation will depend on
        // how we structure the Python agent API
        
        let locals = PyDict::new(py);
        locals.set_item("query", query)?;
        
        // For now, just return a mock response
        Ok("Python bridge initialized - actual integration pending".to_string())
    })
}

/// Check Python environment and dependencies
pub fn check_python_env() -> PyResult<bool> {
    Python::with_gil(|py| {
        // Check if required modules are available
        let modules = vec!["agent_framework", "azure", "mcp"];
        
        for module in modules {
            match py.import(module) {
                Ok(_) => continue,
                Err(_) => {
                    eprintln!("Python module '{}' not found", module);
                    return Ok(false);
                }
            }
        }
        
        Ok(true)
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_python_initialization() {
        assert!(initialize_python().is_ok());
    }

    #[test]
    fn test_check_env() {
        initialize_python().unwrap();
        // This may fail if Python environment is not set up
        let _ = check_python_env();
    }
}
