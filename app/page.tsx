// pages/index.js
"use client";
import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
} from "@mui/material";

const Index = () => {
  const [timestamp, setTimestamp] = useState("");
  const [teamFrameA, setTeamFrameA] = useState({});
  const [teamFrameP, setTeamFrameP] = useState({});
  const [playerStats, setPlayerStats] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/python");
        const data = response.data[0];
        console.log(response);
        setTeamFrameA(data.team_frame_american);
        setTeamFrameP(data.team_frame_percent);
        setTimestamp(data.timestamp);
        setPlayerStats(data.player_stats);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  const renderTable = (teamFrameA: any, teamFrameP: any) => {
    // Check if teamFrameA or teamFrameP are undefined or empty
    if (
      !teamFrameA ||
      !teamFrameP ||
      Object.keys(teamFrameA).length === 0 ||
      Object.keys(teamFrameP).length === 0
    ) {
      return <Typography variant="body1">No data available.</Typography>;
    }

    const combinedData = Object.keys(teamFrameA).map((team) => ({
      Team: team,
      Opp: teamFrameA[team]?.["Opp"] || "-",
      "PD Team Points A": teamFrameA[team]?.["PD Team Points"] || "-",
      "PD Team Points %": teamFrameP[team]?.["PD Team Points"] || "-",
      "PD Opp Points A": teamFrameA[team]?.["PD Opp Points"] || "-",
      "PD Opp Points %": teamFrameP[team]?.["PD Opp Points"] || "-",
      "VEG Team Points A": teamFrameA[team]?.["VEG Team Points"] || "-",
      "VEG Team Points %": teamFrameP[team]?.["VEG Team Points"] || "-",
      "VEG Opp Points A": teamFrameA[team]?.["VEG Opp Points"] || "-",
      "VEG Opp Points %": teamFrameP[team]?.["VEG Opp Points"] || "-",
      "PD Proj Total A": teamFrameA[team]?.["PD Proj Total"] || "-",
      "PD Proj Total %": teamFrameP[team]?.["PD Proj Total"] || "-",
      "VEG Proj Total A": teamFrameA[team]?.["VEG Proj Total"] || "-",
      "VEG Proj Total %": teamFrameP[team]?.["VEG Proj Total"] || "-",
      "PD Over% A": teamFrameA[team]?.["PD Over%"] || "-",
      "PD Over% %": teamFrameP[team]?.["PD Over%"] || "-",
      "PD Under% A": teamFrameA[team]?.["PD Under%"] || "-",
      "PD Under% %": teamFrameP[team]?.["PD Under%"] || "-",
      "PD Proj Winner A": teamFrameA[team]?.["PD Proj Winner"] || "-",
      "PD Proj Winner %": teamFrameP[team]?.["PD Proj Winner"] || "-",
      "PD Proj Spread A": teamFrameA[team]?.["PD Proj Spread"] || "-",
      "PD Proj Spread %": teamFrameP[team]?.["PD Proj Spread"] || "-",
      "PD W Spread A": teamFrameA[team]?.["PD W Spread"] || "-",
      "PD W Spread %": teamFrameP[team]?.["PD W Spread"] || "-",
      "VEG W Spread A": teamFrameA[team]?.["VEG W Spread"] || "-",
      "VEG W Spread %": teamFrameP[team]?.["VEG W Spread"] || "-",
    }));

    const getHeatmapStyle = (value: any) => {
      if (typeof value !== "number") return {}; // Skip non-numeric values

      // Define color gradient thresholds (adjust based on your data range)
      const green = "#56ca85";
      const red = "#ff6f6f";
      const white = "#ffffff";

      // Normalize value between 0 and 1
      const normalizedValue = Math.min(Math.max(value, 0), 1); // Adjust scale as needed

      const backgroundColor = `linear-gradient(
        to right,
        ${red} ${1 - normalizedValue * 100}%,
        ${green} ${normalizedValue * 100}%
      )`;

      return {
        background: backgroundColor,
        color: value > 0.5 ? white : "black", // Contrast for readability
      };
    };

    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {combinedData.length > 0 &&
                Object.keys(combinedData[0]).map((column) => (
                  <TableCell key={column}>{column}</TableCell>
                ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {combinedData.map((row, index) => (
              <TableRow key={index}>
                {Object.values(row).map((value, i) => (
                  <TableCell key={i} style={getHeatmapStyle(value)}>
                    {value}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <div>
      <Typography variant="body1">Last Update: {timestamp} CST</Typography>
      {renderTable(teamFrameA, teamFrameP)}
    </div>
  );
};

export default Index;
