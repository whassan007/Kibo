
import React from "react";
export const DataTable = ({ data, columns }) => (
  <div className="border rounded overflow-hidden">
    <table className="min-w-full text-left text-sm">
      <thead className="bg-gray-50 border-b">
        <tr>{columns.map(c => <th key={c} className="p-4 font-semibold">{c}</th>)}</tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i} className="border-b hover:bg-gray-50">
            {columns.map(c => <td key={c} className="p-4">{row[c]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
