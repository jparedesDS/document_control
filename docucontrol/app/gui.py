from __future__ import annotations

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from docucontrol.config import settings
from docucontrol.services.reporting import MonitoringReportService, ReclamationsService, OVRReportService
from docucontrol.services.returns import GaiaReturnService, ProdocReturnService, TRReturnService

ctk.set_appearance_mode(settings.appearance_mode)
ctk.set_default_color_theme(settings.color_theme)


def load_image(path: Path, size: tuple[int, int]) -> ImageTk.PhotoImage:
    img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


class DocuControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DocuControl App")
        self.service = MonitoringReportService()
        self.reclamations_service = ReclamationsService()
        self.ovr_service = OVRReportService()
        self.tr_service = TRReturnService()
        self.gaia_service = GaiaReturnService()
        self.prodoc_service = ProdocReturnService()

        self._configure_geometry()
        self._build_layout()
        self.show_welcome_page()

    def _configure_geometry(self) -> None:
        self.update_idletasks()
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        width, height = screen_w // 2, screen_h // 2
        x, y = screen_w - width, screen_h - height - 40
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(99, weight=1)

        logo_path = settings.images_dir / "main_logo_img.png"
        self.logo_sidebar = load_image(logo_path, (60, 60))
        ctk.CTkLabel(self.sidebar, image=self.logo_sidebar, text="").grid(row=0, column=0, pady=(15, 8))
        ctk.CTkLabel(self.sidebar, text="DocuControl", font=("Arial", 17, "bold")).grid(row=1, column=0, pady=(0, 20))

        self.btn_monitoring = ctk.CTkButton(
            self.sidebar,
            text="📊 Documentación",
            fg_color="#1E88E5",
            height=45,
            corner_radius=8,
            font=("Arial", 12, "bold"),
            command=self.show_monitoring_page,
        )
        self.btn_monitoring.grid(row=2, column=0, pady=6, padx=10, sticky="ew")

        self.btn_devoluciones = ctk.CTkButton(
            self.sidebar,
            text="📦 Devoluciones",
            fg_color="#43A047",
            height=45,
            corner_radius=8,
            font=("Arial", 12, "bold"),
            command=self.show_devoluciones_page,
        )
        self.btn_devoluciones.grid(row=3, column=0, pady=6, padx=10, sticky="ew")

        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.grid(row=100, column=0, sticky="swe", padx=10, pady=12)

        ctk.CTkButton(
            bottom,
            text="⬅️ Volver",
            fg_color="#757575",
            height=45,
            corner_radius=8,
            font=("Arial", 12, "bold"),
            command=self.show_welcome_page,
        ).pack(fill="x", pady=(0, 4))

        ctk.CTkButton(
            bottom,
            text="🚪 Salir",
            fg_color="#E53935",
            height=45,
            corner_radius=8,
            font=("Arial", 12, "bold"),
            command=self.destroy,
        ).pack(fill="x")

        self.content = ctk.CTkFrame(self, corner_radius=8)
        self.content.grid(row=0, column=1, sticky="nswe", padx=15, pady=15)

    def clear_content(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_welcome_page(self) -> None:
        self.clear_content()
        hero_path = settings.images_dir / "docucontrol_white.png"
        self.hero_image = load_image(hero_path, (450, 280))
        ctk.CTkLabel(self.content, image=self.hero_image, text="").pack(pady=(0, 30))
        ctk.CTkLabel(self.content, text="¡Bienvenido! 👋", font=("Arial", 26, "bold")).pack(pady=(0, 15))
        ctk.CTkLabel(
            self.content,
            text="Gestiona tus documentos de manera rápida y sencilla.\nSelecciona una opción para comenzar.",
            font=("Arial", 16),
            wraplength=450,
            justify="center",
        ).pack(pady=(0, 30))

    def show_monitoring_page(self) -> None:
        self.clear_content()
        ctk.CTkLabel(self.content, text="📊 Control Documental", font=("Arial", 26, "bold")).pack(pady=15)

        btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkButton(
            btn_frame,
            text="Generar Monitoring Report",
            fg_color="#1E88E5",
            height=50,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=self._run_monitoring_report,
        ).grid(row=0, column=0, pady=8, padx=8, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Reclamaciones",
            fg_color="#F39C12",
            height=50,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=self._run_reclamations,
        ).grid(row=1, column=0, pady=8, padx=8, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="OVR Report (Unión)",
            fg_color="#9B59B6",
            height=50,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=lambda: self._run_ovr(mode="union"),
        ).grid(row=2, column=0, pady=8, padx=8, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="OVR Report (Simple)",
            fg_color="#6C3483",
            height=50,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=lambda: self._run_ovr(mode="simple"),
        ).grid(row=3, column=0, pady=8, padx=8, sticky="ew")

    def show_devoluciones_page(self) -> None:
        self.clear_content()
        ctk.CTkLabel(self.content, text="📦 Devolución de documentos", font=("Arial", 26, "bold")).pack(pady=15)

        btn_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Técnicas Reunidas",
            fg_color="#1E88E5",
            height=50,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=lambda: self._run_returns("tr"),
        ).grid(row=0, column=0, padx=10, pady=8)

        ctk.CTkButton(
            btn_frame,
            text="GAIA / Technip",
            fg_color="#43A047",
            height=50,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=lambda: self._run_returns("gaia"),
        ).grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkButton(
            btn_frame,
            text="Wood / Prodoc",
            fg_color="#9B59B6",
            height=50,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=lambda: self._run_returns("prodoc"),
        ).grid(row=0, column=2, padx=10, pady=8)

        ctk.CTkButton(
            self.content,
            text="Abrir plantilla devoluciones",
            fg_color="#6C757D",
            height=40,
            corner_radius=8,
            command=self._open_returns_template,
        ).pack(pady=20)

    def _run_monitoring_report(self) -> None:
        self._show_progress("Generando Monitoring Report...", self._execute_monitoring_report)

    def _execute_monitoring_report(self) -> None:
        try:
            result = self.service.run()
            if settings.copy_prompt_enabled:
                self._prompt_copy(result.output_path)
            messagebox.showinfo("Éxito", f"Reporte generado en:\n{result.output_path}")
            self.show_monitoring_page()
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Error", str(exc))

    def _run_reclamations(self) -> None:
        self._show_progress("Generando correos de reclamaciones...", self._execute_reclamations)

    def _execute_reclamations(self) -> None:
        try:
            emails = self.reclamations_service.generate_emails()
            if not emails:
                messagebox.showinfo("Reclamaciones", "No hay documentos pendientes de reclamación.")
            else:
                self.reclamations_service.send_via_outlook(emails)
                messagebox.showinfo("Reclamaciones", f"Se prepararon {len(emails)} correos en Outlook.")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Error", str(exc))
        finally:
            self.show_monitoring_page()

    def _run_ovr(self, mode: str = "union") -> None:
        label = "Generando OVR..." if mode == "union" else "Generando OVR Simple..."
        self._show_progress(label, lambda: self._execute_ovr(mode))

    def _execute_ovr(self, mode: str) -> None:
        try:
            if mode == "union":
                result = self.ovr_service.generate_union_report()
            else:
                result = self.ovr_service.generate_simple_report()
            messagebox.showinfo("OVR", f"Reporte generado en:\n{result.output_path}")
        except Exception as exc:
            messagebox.showerror("OVR", str(exc))
        finally:
            self.show_monitoring_page()

    def _run_returns(self, vendor: str) -> None:
        labels = {"tr": "Técnicas Reunidas", "gaia": "GAIA / Technip", "prodoc": "Wood / Prodoc"}
        self._show_progress(f"Procesando devoluciones {labels[vendor]}...", lambda: self._execute_returns(vendor))

    def _execute_returns(self, vendor: str) -> None:
        services = {
            "tr": self.tr_service,
            "gaia": self.gaia_service,
            "prodoc": self.prodoc_service,
        }
        try:
            results = services[vendor].run()
            if not results:
                messagebox.showinfo("Devoluciones", "Sin correos nuevos para procesar.")
            else:
                messagebox.showinfo(
                    "Devoluciones",
                    f"Se procesaron {len(results)} correos. Resúmenes en:\n{results[-1].summary_path.parent}",
                )
        except Exception as exc:
            messagebox.showerror("Devoluciones", str(exc))
        finally:
            self.show_devoluciones_page()

    def _open_returns_template(self) -> None:
        template = settings.templates_dir / "plantilla_devoluciones.xlsm"
        if template.exists():
            os.startfile(template)
        else:
            messagebox.showerror("Plantilla", f"No se encontró la plantilla en {template}")

    def _prompt_copy(self, output_path: Path) -> None:
        dest_dir = filedialog.askdirectory(title="Selecciona carpeta destino para copiar el Excel")
        if dest_dir:
            target = Path(dest_dir) / output_path.name
            target.write_bytes(output_path.read_bytes())

    def _show_progress(self, message: str, func) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text=message, font=("Arial", 16, "bold")).pack(pady=(0, 10))
        bar = ctk.CTkProgressBar(container, width=250)
        bar.pack(pady=5)
        bar.start()

        msg_var = ctk.StringVar(value="Inicializando...")
        ctk.CTkLabel(container, textvariable=msg_var, font=("Arial", 11, "italic")).pack(pady=(5, 10))

        steps = [
            "Extrayendo datos...",
            "Resumiendo columnas...",
            "Aplicando cálculos...",
            "Formateando Excel...",
            "Completando...",
        ]
        after_id = {"value": None}

        def animate(index: int = 0):
            if not container.winfo_exists():
                return
            if index < len(steps):
                msg_var.set(steps[index])
                after_id["value"] = container.after(2400, animate, index + 1)
            else:
                msg_var.set("Casi listo...")

        def worker():
            try:
                func()
            finally:
                def stop_bar():
                    if container.winfo_exists():
                        bar.stop()
                        if after_id["value"]:
                            container.after_cancel(after_id["value"])

                self.after(0, stop_bar)

        threading.Thread(target=worker, daemon=True).start()
        animate()


def main() -> None:
    app = DocuControlApp()
    app.mainloop()


if __name__ == "__main__":
    main()
 
