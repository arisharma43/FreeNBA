// pages/api/init_baselines.js
import { init_baselines } from '../../path/to/your/python/script'; // Import your Python script

export default async (req, res) => {
  const { gameModel, playerStats, propFrame, pickFrame, timestamp } = init_baselines();

  res.status(200).json({
    gameModel,
    playerStats,
    propFrame,
    pickFrame,
    timestamp,
  });
};
