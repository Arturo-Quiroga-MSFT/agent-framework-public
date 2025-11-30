import sql from "mssql";
import { Tool } from "@modelcontextprotocol/sdk/types.js";


export class DescribeTableTool implements Tool {
  [key: string]: any;
  name = "describe_table";
  description = "Describes the schema (columns and types) of a specified MSSQL Database table. Supports schema-qualified names like 'schema.table' or just 'table'.";
  inputSchema = {
    type: "object",
    properties: {
      tableName: { type: "string", description: "Name of the table to describe (can be 'schema.table' or just 'table')" },
    },
    required: ["tableName"],
  } as any;

  async run(params: { tableName: string }) {
    try {
      const { tableName } = params;
      
      // Parse schema and table name
      let schemaName = 'dbo';  // Default schema
      let tableNameOnly = tableName;
      
      if (tableName.includes('.')) {
        const parts = tableName.split('.');
        schemaName = parts[0];
        tableNameOnly = parts[1];
      }
      
      const request = new sql.Request();
      const query = `
        SELECT 
          COLUMN_NAME as name, 
          DATA_TYPE as type,
          CHARACTER_MAXIMUM_LENGTH as max_length,
          IS_NULLABLE as nullable,
          COLUMN_DEFAULT as default_value,
          ORDINAL_POSITION as position
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = @schemaName 
          AND TABLE_NAME = @tableName
        ORDER BY ORDINAL_POSITION`;
      
      request.input("schemaName", sql.NVarChar, schemaName);
      request.input("tableName", sql.NVarChar, tableNameOnly);
      
      const result = await request.query(query);
      
      if (result.recordset.length === 0) {
        return {
          success: false,
          message: `Table '${schemaName}.${tableNameOnly}' not found or has no columns`,
        };
      }
      
      return {
        success: true,
        schema: schemaName,
        table: tableNameOnly,
        columns: result.recordset,
      };
    } catch (error) {
      return {
        success: false,
        message: `Failed to describe table: ${error}`,
      };
    }
  }
}
