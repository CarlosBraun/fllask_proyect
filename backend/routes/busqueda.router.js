const express = require("express");
const router = express.Router();
const cors = require("cors");
const busquedaController = require("../controllers/busqueda.controller");

router.use(
  cors({
    allowedOrigins: ["*"],
  })
);

router.post("/formularioCMP", busquedaController.formularioCMP);
router.post("/formularioYear", busquedaController.formularioYear);
router.post("/multipropietarioCMP", busquedaController.multipropietarioCMP);
router.post("/multipropietarioYear", busquedaController.multipropietarioYear);
router.post("/formularioAtencion", busquedaController.formularioAtencion);

module.exports = router;
