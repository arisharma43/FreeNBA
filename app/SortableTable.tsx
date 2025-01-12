// import React, { useState } from "react";
// import {
//   Table,
//   TableBody,
//   TableCell,
//   TableContainer,
//   TableHead,
//   TableRow,
//   Paper,
//   TableSortLabel,
//   Typography,
// } from "@mui/material";

// type SortableTableProps = {
//   data: any[];
//   columns: string[];
//   title: string;
// };

// export function SortableTable({ data, columns, title }: SortableTableProps) {
//   const [sortColumn, setSortColumn] = useState<string | null>(null);
//   const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

//   const handleSort = (column: string) => {
//     if (sortColumn === column) {
//       setSortDirection(sortDirection === "asc" ? "desc" : "asc");
//     } else {
//       setSortColumn(column);
//       setSortDirection("asc");
//     }
//   };

//   const sortedData = [...data].sort((a, b) => {
//     if (sortColumn) {
//       if (a[sortColumn] < b[sortColumn])
//         return sortDirection === "asc" ? -1 : 1;
//       if (a[sortColumn] > b[sortColumn])
//         return sortDirection === "asc" ? 1 : -1;
//     }
//     return 0;
//   });

//   return (
//     <Paper elevation={3} sx={{ padding: 2, marginTop: 3 }}>
//       <Typography variant="h6" gutterBottom>
//         {title}
//       </Typography>
//       <TableContainer>
//         <Table>
//           <TableHead>
//             <TableRow>
//               {columns.map((column) => (
//                 <TableCell key={column} align="center">
//                   <TableSortLabel
//                     active={sortColumn === column}
//                     direction={sortColumn === column ? sortDirection : "asc"}
//                     onClick={() => handleSort(column)}
//                   >
//                     {column}
//                   </TableSortLabel>
//                 </TableCell>
//               ))}
//             </TableRow>
//           </TableHead>
//           <TableBody>
//             {sortedData.map((row, index) => (
//               <TableRow key={index} hover>
//                 {columns.map((column) => (
//                   <TableCell key={column} align="center">
//                     {row[column]}
//                   </TableCell>
//                 ))}
//               </TableRow>
//             ))}
//           </TableBody>
//         </Table>
//       </TableContainer>
//     </Paper>
//   );
// }
"use client";

import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TableSortLabel,
  Typography,
} from "@mui/material";

type SortableTableProps = {
  data: any[];
  columns: string[];
  title: string;
};

export function SortableTable({ data, columns, title }: SortableTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  const sortedData = [...data].sort((a, b) => {
    if (sortColumn) {
      if (a[sortColumn] < b[sortColumn])
        return sortDirection === "asc" ? -1 : 1;
      if (a[sortColumn] > b[sortColumn])
        return sortDirection === "asc" ? 1 : -1;
    }
    return 0;
  });

  const getCellColor = (value: any, column: string) => {
    // Skip coloring for non-numeric values or specific columns
    if (typeof value !== "number" || column === "Team" || column === "Opp") {
      return {};
    }

    // Color logic for percentage columns
    if (
      column.includes("%") ||
      column.includes("Over") ||
      column.includes("Under")
    ) {
      if (value >= 0.55) return { backgroundColor: "#1b5e20", color: "white" };
      if (value <= 0.45) return { backgroundColor: "#b71c1c", color: "white" };
      return { backgroundColor: "#a37f08" };
    }

    // Color logic for point totals and spreads
    if (
      column.includes("Points") ||
      column.includes("Total") ||
      column.includes("Spread")
    ) {
      if (value >= 115) return { backgroundColor: "#1b5e20", color: "white" };
      if (value <= 105) return { backgroundColor: "#b71c1c", color: "white" };
      return { backgroundColor: "#a37f08" };
    }

    return {};
  };

  return (
    <Paper
      elevation={3}
      sx={{
        marginTop: 3,
        backgroundColor: "#1a1a1a",
        borderRadius: "8px",
        overflow: "hidden",
      }}
    >
      <Typography
        variant="h6"
        sx={{
          padding: 2,
          color: "white",
          borderBottom: "1px solid #333",
        }}
      >
        {title}
      </Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ backgroundColor: "#2d2d2d" }}>
              {columns.map((column) => (
                <TableCell
                  key={column}
                  align="center"
                  sx={{
                    color: "white",
                    fontWeight: "bold",
                    borderBottom: "2px solid #444",
                    borderRight: "1px solid #444",
                    padding: "8px",
                    "&:last-child": {
                      borderRight: "none",
                    },
                  }}
                >
                  <TableSortLabel
                    active={sortColumn === column}
                    direction={sortColumn === column ? sortDirection : "asc"}
                    onClick={() => handleSort(column)}
                    sx={{
                      color: "white !important",
                      "&.MuiTableSortLabel-active": {
                        color: "white !important",
                      },
                      "& .MuiTableSortLabel-icon": {
                        color: "white !important",
                      },
                    }}
                  >
                    {column}
                  </TableSortLabel>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedData.map((row, index) => (
              <TableRow
                key={index}
                sx={{
                  "&:nth-of-type(odd)": {
                    backgroundColor: "#262626",
                  },
                  "&:nth-of-type(even)": {
                    backgroundColor: "#1f1f1f",
                  },
                  "&:hover": {
                    backgroundColor: "#333333",
                  },
                }}
              >
                {columns.map((column) => (
                  <TableCell
                    key={column}
                    align="center"
                    sx={{
                      borderRight: "1px solid #444",
                      padding: "6px",
                      color: "white",
                      fontSize: "0.875rem",
                      "&:last-child": {
                        borderRight: "none",
                      },
                      ...getCellColor(row[column], column),
                    }}
                  >
                    {typeof row[column] === "number"
                      ? column.includes("%")
                        ? (row[column] * 100).toFixed(2) + "%"
                        : row[column].toFixed(3)
                      : row[column]}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
