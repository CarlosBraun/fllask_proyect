const express = require("express");
const router = express.Router();
const cors = require("cors");

const tablasController = require("../controllers/tablas.controller");
const busquedaController2 = require("../controllers/lookupDB.controller2")

router.use(
  cors({
    allowedOrigins: ["*"],
  })
);

router.get("/tabla1", tablasController.createFormularioTable);
router.get("/tabla2", tablasController.createEnajenanteTable);
router.get("/tabla3", tablasController.createAdquirenteTable);
router.get("/tabla4", tablasController.createMultipropietarioTable);

router.get("/tablas1", busquedaController2.FormularioTables);
router.get("/tablas2", busquedaController2.AdquirienteTables);
router.get("/tablas3", busquedaController2.EnajenanteTables);
router.get("/tablas4", busquedaController2.MultipropietrioTables);

router.get("/deltablas1", tablasController.deltablas1);
router.get("/deltablas2", tablasController.deltablas2);
router.get("/deltablas3", tablasController.deltablas3);
router.get("/deltablas4", tablasController.deltablas4);

module.exports = router;
