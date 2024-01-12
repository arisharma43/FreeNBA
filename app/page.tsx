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
  const [teamFrameA, setTeamFrameA] = useState([]);
  const [teamFrameP, setTeamFrameP] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/python");
        const data = response.data[0];
        console.log(response);
        setTeamFrameA(data.team_frame_american);
        setTeamFrameP(data.team_frame_percent);
        setTimestamp(data.timestamp);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    
    fetchData();
  }, []);

  return (
    <div>
      <Typography variant="body1">Last Update: {timestamp} CST</Typography>

      <Typography variant="h2">Team Data (Team Frame American)</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Team</TableCell>
              <TableCell>Opponent</TableCell>
              <TableCell>Team Points</TableCell>
              {/* Add other columns as needed */}
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.keys(teamFrameA).map((team) => (
              <TableRow key={team}>
                <TableCell>{team}</TableCell>
                {/* Add other columns as needed */}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="h2">Team Data (Team Frame Percent)</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Team</TableCell>
              <TableCell>Opponent</TableCell>
              <TableCell>Team Points</TableCell>
              {/* Add other columns as needed */}
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.keys(teamFrameP).map((team) => (
              <TableRow key={team}>
                <TableCell>{team}</TableCell>
                {/* Add other columns as needed */}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default Index;
