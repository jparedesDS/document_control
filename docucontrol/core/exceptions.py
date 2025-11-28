class DocuControlError(Exception):
    """Excepción base."""


class DataSourceNotFound(DocuControlError):
    """Archivo de datos no localizado."""


class InvalidDataset(DocuControlError):
    """Los datos no cumplen los requisitos."""


class ReportGenerationError(DocuControlError):
    """Fallo al generar o formatear un reporte."""

