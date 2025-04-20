#!/bin/bash
python server.py & 
gunicorn app:app
