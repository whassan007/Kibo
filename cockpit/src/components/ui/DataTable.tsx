import React, { useState, useMemo } from "react";
import { ChevronDown, ChevronUp, Search } from "lucide-react";
import { Button } from "./Button";
import { EmptyState } from "./EmptyState";

export interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  sortable?: boolean;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (row: T) => string;
  onRowClick?: (row: T) => void;
  searchable?: boolean;
  searchFields?: (keyof T)[];
  itemsPerPage?: number;
}

export function DataTable<T>({ 
  data, columns, keyExtractor, onRowClick, searchable = true, searchFields, itemsPerPage = 10 
}: DataTableProps<T>) {
  const [query, setQuery] = useState("");
  const [sortCol, setSortCol] = useState<number | null>(null);
  const [sortDesc, setSortDesc] = useState(false);
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    if (!query || !searchFields || searchFields.length === 0) return data;
    const lowerQuery = query.toLowerCase();
    return data.filter(row => 
      searchFields.some(field => {
        const val = row[field];
        return val != null && String(val).toLowerCase().includes(lowerQuery);
      })
    );
  }, [data, query, searchFields]);

  const sorted = useMemo(() => {
    if (sortCol === null) return filtered;
    const col = columns[sortCol];
    if (typeof col.accessor === "function") return filtered; // cant sort on arbitrary render function
    
    return [...filtered].sort((a, b) => {
      const valA = a[col.accessor as keyof T];
      const valB = b[col.accessor as keyof T];
      if (valA < valB) return sortDesc ? 1 : -1;
      if (valA > valB) return sortDesc ? -1 : 1;
      return 0;
    });
  }, [filtered, sortCol, sortDesc, columns]);

  const paginated = useMemo(() => {
    const start = (page - 1) * itemsPerPage;
    return sorted.slice(start, start + itemsPerPage);
  }, [sorted, page, itemsPerPage]);

  const totalPages = Math.ceil(sorted.length / itemsPerPage);

  const handleSort = (index: number) => {
    if (!columns[index].sortable) return;
    if (sortCol === index) {
      setSortDesc(!sortDesc);
    } else {
      setSortCol(index);
      setSortDesc(false);
    }
  };

  return (
    <div className="w-full">
      {searchable && (
        <div className="mb-4 relative">
          <Search className="absolute left-3 top-2.5 text-neutral-500 w-5 h-5" />
          <input 
            type="text" 
            placeholder="Search..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(1);
            }}
            className="w-full bg-neutral-900 border border-neutral-800 rounded-md py-2 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
      )}

      {sorted.length === 0 ? (
        <EmptyState title="No Results" description="No data matches your criteria." />
      ) : (
        <div className="overflow-x-auto border border-neutral-800 rounded-lg">
          <table className="w-full text-left text-sm">
            <thead className="bg-neutral-900 border-b border-neutral-800 text-neutral-400">
              <tr>
                {columns.map((col, i) => (
                  <th 
                    key={i} 
                    className={`p-4 font-medium ${col.sortable ? "cursor-pointer hover:text-white" : ""}`}
                    onClick={() => handleSort(i)}
                  >
                    <div className="flex items-center gap-1">
                      {col.header}
                      {col.sortable && sortCol === i && (
                        sortDesc ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800">
              {paginated.map(row => (
                <tr 
                  key={keyExtractor(row)} 
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`hover:bg-neutral-800/50 ${onRowClick ? "cursor-pointer" : ""}`}
                >
                  {columns.map((col, i) => (
                    <td key={i} className="p-4 align-top">
                      {typeof col.accessor === "function" 
                        ? col.accessor(row) 
                        : (row[col.accessor as keyof T] as React.ReactNode)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 text-sm text-neutral-400">
          <div>
            Showing {(page - 1) * itemsPerPage + 1} to {Math.min(page * itemsPerPage, sorted.length)} of {sorted.length}
          </div>
          <div className="flex gap-2">
            <Button 
              variant="secondary" 
              onClick={() => setPage(Math.max(1, page - 1))} 
              disabled={page === 1}
            >
              Previous
            </Button>
            <Button 
              variant="secondary" 
              onClick={() => setPage(Math.min(totalPages, page + 1))} 
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}\n