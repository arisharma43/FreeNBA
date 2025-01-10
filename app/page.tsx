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
import { SortableTable } from "./SortableTable";

const Index = () => {
  const [timestamp, setTimestamp] = useState("");
  const [teamFrameA, setTeamFrameA] = useState({});
  const [teamFrameP, setTeamFrameP] = useState({});
  const [playerStats, setPlayerStats] = useState([]);
  const [propTrendTable, setPropTrendTable] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/python");
        const data = response.data[0];
        console.log(data);
        console.log(data.team_frame_american["PD Team Points"]["NYK"]);
        setTeamFrameA(data.team_frame_american);
        setTeamFrameP(data.team_frame_percent);
        setTimestamp(data.timestamp);
        setPlayerStats(data.player_stats);
        setPropTrendTable(data.prop_trend_table);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  const prepareFrameA = (teamFrameA: any) => {
    if (!teamFrameA || Object.keys(teamFrameA).length === 0) {
      return { data: [], columns: [] };
    }

    // Get all team names from any metric (e.g., "Opp")
    const teams = Object.keys(teamFrameA["Opp"] || {});

    const combinedData = teams.map((team) => ({
      Team: team,
      Opp: teamFrameA["Opp"]?.[team] || "-",
      "PD Team Points": teamFrameA["PD Team Points"]?.[team] || "-",
      "PD Opp Points": teamFrameA["PD Opp Points"]?.[team] || "-",
      "VEG Team Points": teamFrameA["VEG Team Points"]?.[team] || "-",
      "VEG Opp Points": teamFrameA["VEG Opp Points"]?.[team] || "-",
      "PD Proj Total": teamFrameA["PD Proj Total"]?.[team] || "-",
      "VEG Proj Total": teamFrameA["VEG Proj Total"]?.[team] || "-",
      "PD Over Odds": teamFrameA["PD Over Odds"]?.[team] || "-",
      "PD Under Odds": teamFrameA["PD Under Odds"]?.[team] || "-",
      "PD Proj Winner": teamFrameA["PD Proj Winner"]?.[team] || "-",
      "PD Proj Spread": teamFrameA["PD Proj Spread"]?.[team] || "-",
      "PD W Spread": teamFrameA["PD W Spread"]?.[team] || "-",
      "VEG W Spread": teamFrameA["VEG W Spread"]?.[team] || "-",
      "PD Odds": teamFrameA["PD Odds"]?.[team] || "-",
    }));

    const columns = combinedData.length > 0 ? Object.keys(combinedData[0]) : [];
    return { data: combinedData, columns };
  };

  const prepareFrameP = (teamFrameP: any) => {
    if (!teamFrameP || Object.keys(teamFrameP).length === 0) {
      return { data: [], columns: [] };
    }

    // Get all team names from any metric (e.g., "Opp")
    const teams = Object.keys(teamFrameP["Opp"] || {});

    const combinedData = teams.map((team) => ({
      Team: team,
      Opp: teamFrameP["Opp"]?.[team] || "-",
      "PD Team Points": teamFrameP["PD Team Points"]?.[team] || "-",
      "PD Opp Points": teamFrameP["PD Opp Points"]?.[team] || "-",
      "VEG Team Points": teamFrameP["VEG Team Points"]?.[team] || "-",
      "VEG Opp Points": teamFrameP["VEG Opp Points"]?.[team] || "-",
      "PD Proj Total": teamFrameP["PD Proj Total"]?.[team] || "-",
      "VEG Proj Total": teamFrameP["VEG Proj Total"]?.[team] || "-",
      "PD Over%": teamFrameP["PD Over%"]?.[team] || "-",
      "PD Under%": teamFrameP["PD Under%"]?.[team] || "-",
      "PD Proj Winner": teamFrameP["PD Proj Winner"]?.[team] || "-",
      "PD Proj Spread": teamFrameP["PD Proj Spread"]?.[team] || "-",
      "PD W Spread": teamFrameP["PD W Spread"]?.[team] || "-",
      "VEG W Spread": teamFrameP["VEG W Spread"]?.[team] || "-",
      "PD Win%": teamFrameP["PD Win%"]?.[team] || "-",
    }));

    const columns = combinedData.length > 0 ? Object.keys(combinedData[0]) : [];
    return { data: combinedData, columns };
  };

  const americanTable = prepareFrameA(teamFrameA);
  const percentTable = prepareFrameP(teamFrameP);

  return (
    <div>
      <Typography variant="body1">Last Update: {timestamp} CST</Typography>
      {americanTable.data.length > 0 ? (
        <SortableTable
          data={americanTable.data}
          columns={americanTable.columns}
          title="Team Statistics American"
        />
      ) : (
        <Typography variant="body1">No data available for American.</Typography>
      )}
      {percentTable.data.length > 0 ? (
        <SortableTable
          data={percentTable.data}
          columns={percentTable.columns}
          title="Team Statistics Percent"
        />
      ) : (
        <Typography variant="body1">No data available for Percent.</Typography>
      )}
    </div>
  );
};

export default Index;
