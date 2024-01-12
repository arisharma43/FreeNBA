from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import gspread
import json
import pandas as pd
import numpy as np
import streamlit as st
import io
import math

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing) to allow requests from the Next.js app
origins = ["http://localhost:3000"]  # Add the URL of your Next.js app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlayerStats(BaseModel):
    player: str
    prop_type: str
    prop: Optional[float] = None
    mean_outcome: float  # Change the type from str to float
    imp_over: Optional[float] = None
    over_percent: float
    imp_under: Optional[float] = None
    under_percent: float
    bet: Optional[str] = None
    edge: Optional[float] = None


class DataItem(BaseModel):
    team_frame_percent: dict
    team_frame_american: dict
    timestamp: str
    player_stats: List[PlayerStats]


@app.get("/api/python", response_model=List[DataItem])
async def read_data():
    # try:
    gcservice_account = init_conn()
    master_hold = "https://docs.google.com/spreadsheets/d/1Yq0vGriWK-bS79e-bD6_u9pqrYE6Yrlbb_wEkmH-ot0/edit#gid=853878325"
    game_model, player_stats, prop_frame, pick_frame, timestamp = init_baselines(
        gcservice_account, master_hold
    )

    # Extract the relevant data you want to return
    team_frame_percentage = game_model[
        [
            "Team",
            "Opp",
            "Team Points",
            "Opp Points",
            "Proj Total",
            "Proj Spread",
            "Proj Winner",
            "Win%",
        ]
    ]
    team_frame_percentage = team_frame_percentage.set_index("Team")

    team_frame_american = game_model[
        [
            "Team",
            "Opp",
            "Team Points",
            "Opp Points",
            "Proj Total",
            "Proj Spread",
            "Proj Winner",
            "Odds Line",
        ]
    ]
    team_frame_american = team_frame_american.set_index("Team")

    data = {
        "team_frame_percent": team_frame_percentage.to_dict(),
        "team_frame_american": team_frame_american.to_dict(),
        "timestamp": timestamp,
        "player_stats": player_stats_to_list(prop_frame, player_stats),
    }
    # print(data)
    # print(player_stats_to_list(prop_frame, player_stats))
    return [DataItem(**data)]


# except Exception as e:
#     # Handle exceptions, log errors, or customize the response as needed
#     raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


def player_stats_to_list(prop_frame, player_stats):
    finalized_data = clean_data(prop_frame, player_stats)
    player_stats_list = []
    for _, row in finalized_data.iterrows():
        for key, value in row.items():
            if isinstance(value, float) and (
                value == float("inf") or value == float("-inf") or math.isnan(value)
            ):
                row[key] = None
        # print(row)
        player_stats_list.append(
            PlayerStats(
                player=row["Player"],
                prop_type=row["Prop type"],
                prop=row["Prop"],
                mean_outcome=row["Mean_Outcome"],
                imp_over=row["Imp Over"],
                over_percent=row["Over%"],
                imp_under=row["Imp Under"],
                under_percent=row["Under%"],
                bet=row["Bet?"],
                edge=row["Edge"],
            )
        )
    return player_stats_list


def clean_data(prop_frame, player_stats):
    game_format = {"Win%": "{:.2%}"}
    prop_format = {
        "L5 Success": "{:.2%}",
        "L10_Success": "{:.2%}",
        "L20_success": "{:.2%}",
        "Matchup Boost": "{:.2%}",
        "Trending Over": "{:.2%}",
        "Trending Under": "{:.2%}",
        "Implied Over": "{:.2%}",
        "Implied Under": "{:.2%}",
        "Over Edge": "{:.2%}",
        "Under Edge": "{:.2%}",
    }
    prop_table_options = [
        "points",
        "threes",
        "rebounds",
        "assists",
        "blocks",
        "steals",
        "PRA",
        "points+rebounds",
        "points+assists",
        "rebounds+assists",
    ]
    all_sim_vars = [
        "points",
        "rebounds",
        "assists",
        "threes",
        "PRA",
        "points+rebounds",
        "points+assists",
        "rebounds+assists",
    ]
    sim_all_hold = pd.DataFrame(
        columns=[
            "player",
            "prop_type",
            "prop",
            "mean_outcome",
            "imp_over",
            "over_percent",
            "imp_under",
            "under_percent",
            "bet",
            "edge",
        ]
    )
    for prop in all_sim_vars:
        prop_df = prop_frame[
            ["Player", "over_prop", "over_line", "under_line", "prop_type"]
        ]
        prop_df = prop_df.loc[prop_df["prop_type"] == prop]
        prop_df = prop_df[["Player", "over_prop", "over_line", "under_line"]]
        prop_df.rename(columns={"over_prop": "Prop"}, inplace=True)
        prop_df = prop_df.loc[prop_df["Prop"] != 0]
        prop_df["Over"] = np.where(
            prop_df["over_line"] < 0,
            (-(prop_df["over_line"]) / ((-(prop_df["over_line"])) + 101)),
            101 / (prop_df["over_line"] + 101),
        )
        prop_df["Under"] = np.where(
            prop_df["under_line"] < 0,
            (-(prop_df["under_line"]) / ((-(prop_df["under_line"])) + 101)),
            101 / (prop_df["under_line"] + 101),
        )
        df = pd.merge(
            player_stats,
            prop_df,
            how="left",
            left_on=["Player"],
            right_on=["Player"],
        )
        prop_dict = dict(zip(df.Player, df.Prop))
        over_dict = dict(zip(df.Player, df.Over))
        under_dict = dict(zip(df.Player, df.Under))

        total_sims = 5000

        df.fillna(0, inplace=True)
        df.replace([np.inf, -np.inf], 0, inplace=True)

        if prop == "points":
            df["Median"] = df["Points"]
        elif prop == "rebounds":
            df["Median"] = df["Rebounds"]
        elif prop == "assists":
            df["Median"] = df["Assists"]
        elif prop == "threes":
            df["Median"] = df["3P"]
        elif prop == "PRA":
            df["Median"] = df["Points"] + df["Rebounds"] + df["Assists"]
        elif prop == "points+rebounds":
            df["Median"] = df["Points"] + df["Rebounds"]
        elif prop == "points+assists":
            df["Median"] = df["Points"] + df["Assists"]
        elif prop == "rebounds+assists":
            df["Median"] = df["Assists"] + df["Rebounds"]

        flex_file = df
        flex_file["Floor"] = (flex_file["Median"] * 0.25) + (
            flex_file["Minutes"] * 0.25
        )
        flex_file["Ceiling"] = flex_file["Median"] + 10 + (flex_file["Minutes"] * 0.25)
        flex_file["STD"] = flex_file["Median"] / 4
        flex_file["Prop"] = flex_file["Player"].map(prop_dict)
        flex_file = flex_file[["Player", "Prop", "Floor", "Median", "Ceiling", "STD"]]

        hold_file = flex_file
        overall_file = flex_file
        prop_file = flex_file

        overall_players = overall_file[["Player"]]

        for x in range(0, total_sims):
            prop_file[x] = prop_file["Prop"]

        prop_file = prop_file.drop(
            ["Player", "Prop", "Floor", "Median", "Ceiling", "STD"], axis=1
        )

        for x in range(0, total_sims):
            overall_file[x] = np.random.normal(
                overall_file["Median"], overall_file["STD"]
            )

        overall_file = overall_file.drop(
            ["Player", "Prop", "Floor", "Median", "Ceiling", "STD"], axis=1
        )

        players_only = hold_file[["Player"]]

        player_outcomes = pd.merge(
            players_only, overall_file, left_index=True, right_index=True
        )

        prop_check = overall_file - prop_file

        players_only["Mean_Outcome"] = overall_file.mean(axis=1)
        players_only["10%"] = overall_file.quantile(0.1, axis=1)
        players_only["90%"] = overall_file.quantile(0.9, axis=1)
        players_only["Over"] = prop_check[prop_check > 0].count(axis=1) / float(
            total_sims
        )
        players_only["Imp Over"] = players_only["Player"].map(over_dict)
        players_only["Over%"] = players_only[["Over", "Imp Over"]].mean(axis=1)
        players_only["Under"] = prop_check[prop_check < 0].count(axis=1) / float(
            total_sims
        )
        players_only["Imp Under"] = players_only["Player"].map(under_dict)
        players_only["Under%"] = players_only[["Under", "Imp Under"]].mean(axis=1)
        players_only["Prop"] = players_only["Player"].map(prop_dict)
        players_only["Prop_avg"] = players_only["Prop"].mean() / 100
        players_only["prop_threshold"] = 0.10
        players_only = players_only.loc[players_only["Mean_Outcome"] > 0]
        players_only["Over_diff"] = players_only["Over%"] - players_only["Imp Over"]
        players_only["Under_diff"] = players_only["Under%"] - players_only["Imp Under"]
        players_only["Bet_check"] = np.where(
            players_only["Over_diff"] > players_only["Under_diff"],
            players_only["Over_diff"],
            players_only["Under_diff"],
        )
        players_only["Bet_suggest"] = np.where(
            players_only["Over_diff"] > players_only["Under_diff"], "Over", "Under"
        )
        players_only["Bet?"] = np.where(
            players_only["Bet_check"] >= players_only["prop_threshold"],
            players_only["Bet_suggest"],
            "No Bet",
        )
        players_only["Edge"] = players_only["Bet_check"]
        players_only["Prop type"] = prop

        players_only["Player"] = hold_file[["Player"]]

        leg_outcomes = players_only[
            [
                "Player",
                "Prop type",
                "Prop",
                "Mean_Outcome",
                "Imp Over",
                "Over%",
                "Imp Under",
                "Under%",
                "Bet?",
                "Edge",
            ]
        ]

        sim_all_hold = pd.concat([sim_all_hold, leg_outcomes], ignore_index=True)

        final_outcomes = sim_all_hold
        # print(final_outcomes)
        return final_outcomes


def init_conn():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = {
        "type": "service_account",
        "project_id": "model-sheets-connect",
        "private_key_id": "0e0bc2fdef04e771172fe5807392b9d6639d945e",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDiu1v/e6KBKOcK\ncx0KQ23nZK3ZVvADYy8u/RUn/EDI82QKxTd/DizRLIV81JiNQxDJXSzgkbwKYEDm\n48E8zGvupU8+Nk76xNPakrQKy2Y8+VJlq5psBtGchJTuUSHcXU5Mg2JhQsB376PJ\nsCw552K6Pw8fpeMDJDZuxpKSkaJR6k9G5Dhf5q8HDXnC5Rh/PRFuKJ2GGRpX7n+2\nhT/sCax0J8jfdTy/MDGiDfJqfQrOPrMKELtsGHR9Iv6F4vKiDqXpKfqH+02E9ptz\nBk+MNcbZ3m90M8ShfRu28ebebsASfarNMzc3dk7tb3utHOGXKCf4tF8yYKo7x8BZ\noO9X4gSfAgMBAAECggEAU8ByyMpSKlTCF32TJhXnVJi/kS+IhC/Qn5JUDMuk4LXr\naAEWsWO6kV/ZRVXArjmuSzuUVrXumISapM9Ps5Ytbl95CJmGDiLDwRL815nvv6k3\nUyAS8EGKjz74RpoIoH6E7EWCAzxlnUgTn+5oP9Flije97epYk3H+e2f1f5e1Nn1d\nYNe8U+1HqJgILcxA1TAUsARBfoD7+K3z/8DVPHI8IpzAh6kTHqhqC23Rram4XoQ6\nzj/ZdVBjvnKuazETfsD+Vl3jGLQA8cKQVV70xdz3xwLcNeHsbPbpGBpZUoF73c65\nkAXOrjYl0JD5yAk+hmYhXr6H9c6z5AieuZGDrhmlFQKBgQDzV6LRXmjn4854DP/J\nI82oX2GcI4eioDZPRukhiQLzYerMQBmyqZIRC+/LTCAhYQSjNgMa+ZKyvLqv48M0\n/x398op/+n3xTs+8L49SPI48/iV+mnH7k0WI/ycd4OOKh8rrmhl/0EWb9iitwJYe\nMjTV/QxNEpPBEXfR1/mvrN/lVQKBgQDuhomOxUhWVRVH6x03slmyRBn0Oiw4MW+r\nrt1hlNgtVmTc5Mu+4G0USMZwYuOB7F8xG4Foc7rIlwS7Ic83jMJxemtqAelwOLdV\nXRLrLWJfX8+O1z/UE15l2q3SUEnQ4esPHbQnZowHLm0mdL14qSVMl1mu1XfsoZ3z\nJZTQb48CIwKBgEWbzQRtKD8lKDupJEYqSrseRbK/ax43DDITS77/DWwHl33D3FYC\nMblUm8ygwxQpR4VUfwDpYXBlklWcJovzamXpSnsfcYVkkQH47NuOXPXPkXQsw+w+\nDYcJzeu7F/vZqk9I7oBkWHUrrik9zPNoUzrfPvSRGtkAoTDSwibhoc5dAoGBAMHE\nK0T/ANeZQLNuzQps6S7G4eqjwz5W8qeeYxsdZkvWThOgDd/ewt3ijMnJm5X05hOn\ni4XF1euTuvUl7wbqYx76Wv3/1ZojiNNgy7ie4rYlyB/6vlBS97F4ZxJdxMlabbCW\n6b3EMWa4EVVXKoA1sCY7IVDE+yoQ1JYsZmq45YzPAoGBANWWHuVueFGZRDZlkNlK\nh5OmySmA0NdNug3G1upaTthyaTZ+CxGliwBqMHAwpkIRPwxUJpUwBTSEGztGTAxs\nWsUOVWlD2/1JaKSmHE8JbNg6sxLilcG6WEDzxjC5dLL1OrGOXj9WhC9KX3sq6qb6\nF/j9eUXfXjAlb042MphoF3ZC\n-----END PRIVATE KEY-----\n",
        "client_email": "gspread-connection@model-sheets-connect.iam.gserviceaccount.com",
        "client_id": "100369174533302798535",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gspread-connection%40model-sheets-connect.iam.gserviceaccount.com",
    }

    gc_con = gspread.service_account_from_dict(credentials)

    return gc_con


gcservice_account = init_conn()

master_hold = "https://docs.google.com/spreadsheets/d/1Yq0vGriWK-bS79e-bD6_u9pqrYE6Yrlbb_wEkmH-ot0/edit#gid=853878325"

game_format = {"Win%": "{:.2%}"}
prop_format = {
    "L5 Success": "{:.2%}",
    "L10_Success": "{:.2%}",
    "L20_success": "{:.2%}",
    "Matchup Boost": "{:.2%}",
    "Trending Over": "{:.2%}",
    "Trending Under": "{:.2%}",
    "Implied Over": "{:.2%}",
    "Implied Under": "{:.2%}",
    "Over Edge": "{:.2%}",
    "Under Edge": "{:.2%}",
}
prop_table_options = [
    "points",
    "threes",
    "rebounds",
    "assists",
    "blocks",
    "steals",
    "PRA",
    "points+rebounds",
    "points+assists",
    "rebounds+assists",
]
all_sim_vars = [
    "points",
    "rebounds",
    "assists",
    "threes",
    "PRA",
    "points+rebounds",
    "points+assists",
    "rebounds+assists",
]
sim_all_hold = pd.DataFrame(
    columns=[
        "Player",
        "Prop type",
        "Prop",
        "Mean_Outcome",
        "Imp Over",
        "Over%",
        "Imp Under",
        "Under%",
        "Bet?",
        "Edge",
    ]
)


def init_baselines(gcservice_account, master_hold):
    sh = gcservice_account.open_by_url(master_hold)
    worksheet = sh.worksheet("Betting Model Clean")
    raw_display = pd.DataFrame(worksheet.get_all_records())
    raw_display.replace("#DIV/0!", np.nan, inplace=True)
    raw_display["Win%"] = (
        raw_display["Win%"].replace({"%": ""}, regex=True).astype(float) / 100
    )
    game_model = raw_display.dropna()

    worksheet = sh.worksheet("DK_Build_Up")
    raw_display = pd.DataFrame(worksheet.get_all_records())
    raw_display.replace("", np.nan, inplace=True)
    raw_display.rename(columns={"Name": "Player"}, inplace=True)
    raw_display = raw_display[
        [
            "Player",
            "Position",
            "Team",
            "Opp",
            "Minutes",
            "3P",
            "Points",
            "Rebounds",
            "Assists",
            "Steals",
            "Blocks",
            "Turnovers",
            "Fantasy",
        ]
    ]
    player_stats = raw_display[raw_display["Minutes"] > 0]

    player_stats["Player"].replace(
        [
            "Jaren Jackson",
            "Nic Claxton",
            "Jabari Smith",
            "Lu Dort",
            "Moe Wagner",
            "Kyle Kuzma",
            "Trey Murphy",
            "Cameron Thomas",
        ],
        [
            "Jaren Jackson Jr.",
            "Nicolas Claxton",
            "Jabari Smith Jr.",
            "Luguentz Dort",
            "Moritz Wagner",
            "Kyle Kuzma Jr.",
            "Trey Murphy III",
            "Cam Thomas",
        ],
        inplace=True,
    )

    worksheet = sh.worksheet("Timestamp")
    timestamp = worksheet.acell("A1").value

    worksheet = sh.worksheet("Prop_Frame")
    raw_display = pd.DataFrame(worksheet.get_all_records())
    raw_display.replace("", np.nan, inplace=True)
    prop_frame = raw_display.dropna(subset="Player")

    worksheet = sh.worksheet("Pick6_ingest")
    raw_display = pd.DataFrame(worksheet.get_all_records())
    raw_display.replace("", np.nan, inplace=True)
    pick_frame = raw_display.dropna(subset="Player")

    prop_frame["Player"].replace(
        [
            "Jaren Jackson",
            "Nic Claxton",
            "Jabari Smith",
            "Lu Dort",
            "Moe Wagner",
            "Kyle Kuzma",
            "Trey Murphy",
            "Cameron Thomas",
        ],
        [
            "Jaren Jackson Jr.",
            "Nicolas Claxton",
            "Jabari Smith Jr.",
            "Luguentz Dort",
            "Moritz Wagner",
            "Kyle Kuzma Jr.",
            "Trey Murphy III",
            "Cam Thomas",
        ],
        inplace=True,
    )
    pick_frame["Player"].replace(
        [
            "Jaren Jackson",
            "Nic Claxton",
            "Jabari Smith",
            "Lu Dort",
            "Moe Wagner",
            "Kyle Kuzma",
            "Trey Murphy",
            "Cameron Thomas",
        ],
        [
            "Jaren Jackson Jr.",
            "Nicolas Claxton",
            "Jabari Smith Jr.",
            "Luguentz Dort",
            "Moritz Wagner",
            "Kyle Kuzma Jr.",
            "Trey Murphy III",
            "Cam Thomas",
        ],
        inplace=True,
    )
    return game_model, player_stats, prop_frame, pick_frame, timestamp


def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")
