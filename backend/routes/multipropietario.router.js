const express = require("express");
const router = express.Router();
const cors = require("cors");

const multipropietarioController = require("../controllers/multipropietario.controller");

router.use(
  cors({
    allowedOrigins: ["*"],
  })
);

router.post("/crear", multipropietarioController.createMultipropietario);

module.exports = router;
