.PHONY: all convert train evaluate package

all: convert train evaluate package

convert:
	mkdir -p training/corpus
	python training/scripts/convert.py en training/assets/yes_no_training.jsonl training/corpus/train.spacy
	python training/scripts/convert.py en training/assets/yes_no_eval.jsonl training/corpus/dev.spacy

train:
	python -m spacy train training/configs/config.cfg --output training/output/ --paths.train training/corpus/train.spacy --paths.dev training/corpus/dev.spacy --nlp.lang en --gpu-id 0

evaluate:
	python -m spacy evaluate training/output/model-best training/corpus/dev.spacy --output training/output/metrics.json

package:
	python -m spacy package training/output/model-best training/packages --name yes_no_detection --version 0.1.4 --force

