## DocuControl (refactor)

Nueva estructura modular para los flujos de control documental, reportes y devoluciones.

### Capas
- `docucontrol/app`: GUI CustomTkinter.
- `docucontrol/cli`: comandos para ejecución sin interfaz.
- `docucontrol/services`: lógica de negocio (reportes, reclamaciones, devoluciones).
- `docucontrol/infra`: adaptadores Excel/Outlook/Datos.
- `docucontrol/legacy`: utilidades heredadas reutilizadas por los servicios.
- `docucontrol/config`: settings y logging.

### Setup
```bash
cd docucontrol_refactor
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Ejecución rápida
- GUI: `python -m docucontrol.app.gui`
- Monitoring report: `python -m docucontrol.cli.monitoring --date 28-11-2025`
- Reclamaciones: `python -m docucontrol.cli.reclamations --send`
- OVR: `python -m docucontrol.cli.ovr --mode union`
- Devoluciones TR/GAIA/PRODOC: `python -m docucontrol.cli.returns --vendor tr|gaia|prodoc`

### Datos
Coloca los excels fuente en `data/input/` (`data_erp.xlsx`, `consulta_erp.xlsx`, `data_tags.xlsx`).  
Los reportes salen en `data/output/`, y las devoluciones en `data/returns/<VENDOR>/<fecha>` salvo que configures `DOCUCONTROL_RETURNS_DIR`.

### Próximos pasos sugeridos
- Migrar el resto de flujos externos (Sendoc/Aconex) a los mismos servicios.
- Añadir pipelines CI con `pytest`, `ruff`, `black`.
- Empaquetar en una rueda o instalador interno.
 
