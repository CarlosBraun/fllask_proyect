const mysql = require("mysql2/promise");
const connection = require("../database");

// Función para verificar si una cadena es una fecha válida en el formato 'YYYY-MM-DD'
const isValidDate = (dateString) => {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  return regex.test(dateString) && !isNaN(Date.parse(dateString));
};

const formularioController = {
  createFormulario: async (req, res) => {
    let connection;
    try {
      // Obtén los formularios del cuerpo de la solicitud
      const formularios = req.body["F2890"];

      // Obtiene una nueva conexión
      connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });

      // Inicia la transacción manualmente
      await connection.beginTransaction();

      // Consulta para obtener el último número de atención insertado
      const lastNumeroAtencionSQL = `
        SELECT numero_atencion FROM Formulario ORDER BY id DESC LIMIT 1
      `;

      // Ejecuta la consulta para obtener el último número de atención
      const [lastNumeroAtencionRows] = await connection.query(
        lastNumeroAtencionSQL
      );

      // Calcula el próximo número de atención
      let numeroAtencion = 1;
      if (lastNumeroAtencionRows.length > 0) {
        const lastNumeroAtencion = Number(
          lastNumeroAtencionRows[0].numero_atencion
        );
        numeroAtencion = isNaN(lastNumeroAtencion) ? 1 : lastNumeroAtencion;
      }

      // Itera sobre cada formulario recibido
      await Promise.all(
        formularios.map(async (formulario) => {
          try {
            // Verifica si bienRaiz está presente en el formulario
            numeroAtencion = numeroAtencion + 1;
            if (!formulario.bienRaiz) {
              throw new Error("bienRaiz is not defined in the form");
            }

            // Extrae los datos específicos del formulario
            const {
              _comment,
              CNE,
              bienRaiz,
              enajenantes = [],
              adquirentes = [],
              fojas,
              fechaInscripcion,
              nroInscripcion,
            } = formulario;

            // Extrae los datos específicos de bienRaiz
            const { comuna, manzana, predio } = bienRaiz;

            // Verifica si la fecha de inscripción es válida
            if (!isValidDate(fechaInscripcion)) {
              throw new Error("Fecha de inscripción inválida");
            }
            console.log(numeroAtencion);
            // Construye la consulta SQL para insertar el formulario
            const insertFormularioSQL = `
              INSERT INTO Formulario 
                (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion, numero_inscripcion) 
              VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?)
            `;
            console.log(numeroAtencion);
            // Ejecuta la consulta SQL para insertar el formulario
            const [formularioResult] = await connection.query(
              insertFormularioSQL,
              [
                numeroAtencion,
                CNE,
                comuna,
                manzana,
                predio,
                fojas,
                fechaInscripcion,
                nroInscripcion,
              ]
            );

            // Incrementa el número de atención para el próximo formulario

            // Obtiene el ID del formulario recién insertado
            const formularioId = formularioResult.insertId;

            // Construye las consultas SQL para insertar los enajenantes y adquirentes
            const insertEnajenantesSQL = `
              INSERT INTO Enajenante (runrut, porc_derecho, formulario_id) 
              VALUES (?, ?, ?)
            `;
            const insertAdquirentesSQL = `
              INSERT INTO Adquirente (runrut_adq, porc_derecho_adq, formulario_id) 
              VALUES (?, ?, ?)
            `;

            // Ejecuta las consultas SQL para insertar los enajenantes
            await Promise.all(
              enajenantes.map(async (enajenante) => {
                await connection.query(insertEnajenantesSQL, [
                  enajenante.RUNRUT,
                  enajenante.porcDerecho,
                  formularioId,
                ]);
              })
            );

            // Ejecuta las consultas SQL para insertar los adquirentes
            await Promise.all(
              adquirentes.map(async (adquirente) => {
                await connection.query(insertAdquirentesSQL, [
                  adquirente.RUNRUT,
                  adquirente.porcDerecho,
                  formularioId,
                ]);
              })
            );
          } catch (error) {
            // Maneja el error y continúa con el siguiente formulario
            console.error("Error processing formulario:", error);
          }
        })
      );

      // Commit de la transacción
      await connection.commit();

      // Envía una respuesta exitosa
      res.json({ msg: "Formularios creados exitosamente" });
    } catch (error) {
      // Rollback de la transacción en caso de error
      if (connection) {
        await connection.rollback();
      }
      // Envía un mensaje de error si ocurre algún problema
      res.status(500).json({ msg: error.message });
    } finally {
      // Libera la conexión
      if (connection) {
        connection.end();
      }
    }
  },
};

module.exports = formularioController;
