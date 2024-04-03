const express = require("express");
const router = express.Router();
const cors = require("cors");

const formularioController = require("../controllers/formulario.controller");

router.use(
  cors({
    allowedOrigins: ["*"],
  })
);

router.post("/crear", formularioController.createFormulario);

module.exports = router;
