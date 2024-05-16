const mysql = require("mysql2/promise");
const pool = require("../database");
const lookupDBController = require("./lookupDB.controller");
const insertDBController = require("./insertDB.controller");

// Función para verificar si una cadena es una fecha válida en el formato 'YYYY-MM-DD'
const isValidDate = (dateString) => {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  return regex.test(dateString) && !isNaN(Date.parse(dateString));
};

const multipropietarioController = {
  createMultipropietario: async (req, res) => {
    try {
      const { comuna, manzana, predio } = req.body;
      const formularios = await lookupDBController.FormularioCMP(
        comuna,
        manzana,
        predio
      );

      for (let formulario of formularios) {
        await insertDBController.Multipropietrio(
          formulario.comuna,
          formulario.manzana,
          formulario.predio,
          formulario.runrut,
          formulario.porc_derecho,
          formulario.fojas,
          formulario.fecha_inscripcion,
          new Date(formulario.fecha_inscripcion).getFullYear(),
          formulario.numero_inscripcion,
          formulario.fecha_inscripcion,
          null
        );
      }

      res
        .status(200)
        .send({ message: "Multipropietario entries created successfully." });
    } catch (error) {
      res.status(500).json({ msg: error.message });
    }
  },
  buscarMultipropietario: async (req, res) => {
    let connection;
    try {
      const datos = req.body;
      const connection = await pool.getConnection();
      await connection.beginTransaction();

      try {
        const { comuna, manzana, predio, ano } = datos;
        const transactionData = await lookupDBController.MultipropietrioCMP(
          comuna,
          manzana,
          predio
        );
        const data_filtrada = [];
        for (let i = 0; i < transactionData.length; i++) {
          const elemento = transactionData[i];
          if (
            elemento.ano_vigencia_i <= ano &&
            (elemento.ano_vigencia_f === "" || ano <= elemento.ano_vigencia_f)
          ) {
            data_filtrada.push(elemento);
          }
        }
        console.log(data_filtrada);
        res.json(data_filtrada);
      } catch (error) {
        console.error("Error processing formulario:", error);
      }
      await connection.commit();
    } catch (error) {
      if (connection) {
        await connection.rollback();
      }
    } finally {
      if (connection) {
        connection.release();
      }
    }
  },
  createFormulario: async (req, res) => {
    let connection;
    try {
      const multipropietarios = req.body;
      const connection = await pool.getConnection();
      await connection.beginTransaction();
      await Promise.all(
        multipropietarios.map(async (multipropietario) => {
          try {
            const {
              comuna,
              manzana,
              predio,
              run,
              derecho,
              fojas,
              fecha_inscripcion,
              ano_inscripccion,
              numero_inscripcion,
              ano_vigencia_i,
              ano_vigencia_f,
              status,
            } = multipropietario;
            console.log(multipropietario);
            const transactionData = await insertDBController.Multipropietrio(
              comuna,
              manzana,
              predio,
              run,
              derecho,
              fojas,
              fecha_inscripcion,
              ano_inscripccion,
              numero_inscripcion,
              ano_vigencia_i,
              ano_vigencia_f,
              status
            );
            console.log(transactionData);
          } catch (error) {
            console.error("Error processing formulario:", error);
          }
        })
      );

      await connection.commit();

      res.json({ msg: "Formularios creados exitosamente" });
    } catch (error) {
      if (connection) {
        await connection.rollback();
      }
    } finally {
      if (connection) {
        connection.release();
      }
    }
  },
};

module.exports = multipropietarioController;
