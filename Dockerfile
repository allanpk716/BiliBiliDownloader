# For more information, please refer to https://aka.ms/vscode-docker-python
FROM danielkelleher/pyppeteer_spider:1.03

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install pip requirements
ADD requirements.txt .
RUN python3 -m pip install -r requirements.txt

WORKDIR /app
ADD . /app
COPY fake_agent /app/fake_agent
COPY download /app/download
COPY Logs /app/Logs

# RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
#     && echo 'Asia/Shanghai' >/etc/timezone

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
# RUN useradd appuser \
#     && chown -R appuser:100 /app
# USER appuser
RUN chown -R 0 /app \
    # 提前下载 chrome
    && python3 dockerbuild.py
    
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python3", "Main.py"]
