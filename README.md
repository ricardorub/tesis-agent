<div align="center">

# Tesis Agent 

### Un asistente inteligente para tesis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Cerebras](https://img.shields.io/badge/Cerebras_AI-FF6B35?style=for-the-badge&logo=ai&logoColor=white)](https://cerebras.ai)

**Thesis Agent** es una aplicación web de asesoría académica que conecta estudiantes universitarios con un chatbot potenciado por IA. El asistente no solo responde preguntas generales: lee y comprende los documentos PDF de la tesis del usuario y da respuestas contextualizadas gracias a un RAG construido desde cero.

El proyecto abarca backend, frontend, base de datos, modelos de lenguaje, embeddings vectoriales y un panel de análisis de datos — todo integrado en una sola plataforma.

</div>

---



##  Lo que hace que este proyecto destaque

###  Chat con memoria y contexto real
No es un simple chatbot. El usuario puede manejar múltiples sesiones y los títulos se generan automáticamente por el modelo según el tema de la consulta.

###  RAG sobre documentos propios
Este sistema indexa PDFs académicos usando embeddings semánticos y los almacena en un índice faiss. Cuando el usuario hace una pregunta, el sistema recupera los fragmentos más relevantes y se los inyecta al LLM logrando respuestas precisas y fundamentadas en el contenido real de la tesis.

### Dashboard analítico completo
El panel de moderador muestra en tiempo real: evolución temporal de usuarios y chats, distribución por universidad, género, nivel académico y rango de edad, además de los resultados de satisfacción — todo en gráficos interactivos con Chart.js.

### Sistema de roles multicapa
Cuenta con tres niveles de acceso como `user`, `moderator`, `administrator`, las contraseñas protegidas por bcrypt.

---






---


## Vistas de la aplicación



---

<div align="center">

**Construido con curiosidad, café y muchas horas de creatividad** 

</div>