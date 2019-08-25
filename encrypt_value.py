#!/usr/bin/env python
import boto3
import os
import logging
import sys
import json
import base64
import argparse
import requests

parser = argparse.ArgumentParser(description='encrypt a string using the KMS key')
parser.add_argument('-v', '--val', action='store', dest='val', help='A string value that will be encrypted')
parser.add_argument('-r', '--region', action='store', dest='region', help='The AWS region where the KMS key located')
parser.add_argument('-k', '--key', action='store', dest='key', help='The KMS key ID that will use to encrypt the string value')

args = parser.parse_args()


region = args.region
kmsid = args.key

kms_client = boto3.client('kms', region_name=region)


def setup_logging():
  logger = logging.getLogger()
  for h in logger.handlers:
    logger.removeHandler(h)

  h = logging.StreamHandler(sys.stdout)

  FORMAT = '%(asctime)s %(message)s'
  h.setFormatter(logging.Formatter(FORMAT))
  logger.addHandler(h)
  logger.setLevel(logging.INFO)

  return logger


def encrypt_data(s_key, logger):

  try:
    response = kms_client.encrypt(
            KeyId=kmsid,
            Plaintext=s_key
      )
    return response
    logger.info("Encrypting data")
  except Exception as err:
    logger.error(err)



if __name__ == "__main__":

    logger = setup_logging()

    s_key = args.val

    encrypted_key = encrypt_data(s_key, logger)
    binary_key = encrypted_key['CiphertextBlob']
    encrypted_secret = base64.b64encode(binary_key)
    binary_decoded = encrypted_secret.decode()
   
    print(binary_decoded)
    print("------------")
