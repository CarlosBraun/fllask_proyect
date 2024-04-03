const express = require("express");
const router = express.Router();
const cors = require("cors");
const busquedaController = require("../controllers/busqueda.controller");

router.use(
  cors({
    allowedOrigins: ["*"],
  })
);

router.post("/", busquedaController.busqueda);
router.post("/atencion", busquedaController.atencion);

module.exports = router;
