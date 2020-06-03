
FROM python:3.6
RUN pip install scikit-learn
RUN pip install opencv-python
RUN pip install scikit-image
RUN pip install pandas
RUN pip install --no-cache-dir torch==1.2.0 torchvision==0.4.0 -f https://download.pytorch.org/whl/torch_stable.html
RUN mkdir /test/
RUN mkdir /train/
COPY predict_model.py /usr/local/bin/
COPY run.sh /
COPY models/ /models/
COPY output/ /output/
COPY retinanet/ /usr/local/bin/retinanet/
COPY sampleUtilitiesCode/ /usr/local/bin/sampleUtilitiesCode/

RUN chmod a+x /usr/local/bin/predict_model.py
RUN chmod a+x /run.sh

ENTRYPOINT ["/bin/bash", "/run.sh"]






