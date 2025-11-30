import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { Tool } from '@modelcontextprotocol/sdk/types.js';

/**
 * PythonExecuteTool - Execute Python code for data visualization and analysis
 * Useful for generating charts, graphs, and statistical analysis from SQL query results
 */
export class PythonExecuteTool implements Tool {
  [key: string]: any;
  name = 'python_execute';
  description = `Execute Python code to generate visualizations and perform data analysis.
  
Use this tool to:
- Generate charts (matplotlib, seaborn, plotly)
- Create statistical visualizations
- Perform data transformations
- Generate reports with pandas

The code should save output files (PNG, SVG, CSV, etc.) which will be returned to the user.
Common packages available: matplotlib, seaborn, pandas, numpy, plotly

Example usage:
1. Query data using run_query or read_data
2. Pass data to this tool with Python code
3. Code generates visualization and saves to file
4. Tool returns file information`;

  inputSchema = {
    type: 'object' as const,
    properties: {
      code: {
        type: 'string',
        description: 'Python code to execute. Should include imports and save output files.',
      },
      data: {
        type: 'string',
        description: 'Optional JSON string of data to pass to the script (will be available as DATA variable)',
      },
      filename: {
        type: 'string',
        description: 'Output filename (e.g., "fragmentation_chart.png"). Must include extension.',
      },
    },
    required: ['code', 'filename'],
  } as any;

  async run(args: {
    code: string;
    data?: string;
    filename: string;
  }): Promise<{ content: Array<{ type: string; text: string }> }> {
    try {
      // Validate filename (security)
      const safeFilename = path.basename(args.filename);
      if (safeFilename !== args.filename || args.filename.includes('..')) {
        throw new Error('Invalid filename. Must be a simple filename without path traversal.');
      }

      // Create output directory if it doesn't exist
      const outputDir = path.join(process.cwd(), 'python_outputs');
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      const outputPath = path.join(outputDir, safeFilename);

      // Prepare Python script
      let fullScript = '';
      
      // Add data if provided
      if (args.data) {
        fullScript += `import json\n`;
        fullScript += `DATA = json.loads('''${args.data.replace(/'/g, "\\'")}''')\n\n`;
      }

      // Add user code
      fullScript += args.code;

      // Ensure the code saves to the correct output path
      if (!args.code.includes(safeFilename) && !args.code.includes('plt.savefig')) {
        fullScript += `\n\n# Auto-save if not explicitly saved\nimport matplotlib.pyplot as plt\nplt.savefig('${outputPath}')\n`;
      } else if (args.code.includes(safeFilename) && !path.isAbsolute(safeFilename)) {
        // Replace relative filename with absolute path
        fullScript = fullScript.replace(
          new RegExp(`['"]${safeFilename}['"]`, 'g'),
          `'${outputPath}'`
        );
      }

      // Create temporary Python file
      const tempScriptPath = path.join(outputDir, `temp_script_${Date.now()}.py`);
      fs.writeFileSync(tempScriptPath, fullScript);

      try {
        // Execute Python script with timeout
        const startTime = Date.now();
        const result = execSync(`python3 "${tempScriptPath}"`, {
          encoding: 'utf-8',
          timeout: 30000, // 30 second timeout
          maxBuffer: 10 * 1024 * 1024, // 10MB buffer
          cwd: outputDir,
        });
        const executionTime = Date.now() - startTime;

        // Check if output file was created
        if (!fs.existsSync(outputPath)) {
          throw new Error(`Output file not created: ${safeFilename}`);
        }

        // Get file stats
        const stats = fs.statSync(outputPath);
        const fileSizeKB = (stats.size / 1024).toFixed(2);

        // Clean up temp script
        fs.unlinkSync(tempScriptPath);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: true,
                executionTimeMs: executionTime,
                filename: safeFilename,
                filepath: outputPath,
                filesizeKB: fileSizeKB,
                output: result.trim() || '(no console output)',
                message: `Visualization saved to ${safeFilename}`,
              }, null, 2),
            },
          ],
        };
      } finally {
        // Clean up temp script if it still exists
        if (fs.existsSync(tempScriptPath)) {
          fs.unlinkSync(tempScriptPath);
        }
      }
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: `Python execution failed: ${error.message}`,
              stderr: error.stderr?.toString() || '',
            }, null, 2),
          },
        ],
      };
    }
  }
}
