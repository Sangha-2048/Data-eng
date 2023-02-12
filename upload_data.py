#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
import argparse 
import os
from time import time

def main(params):
	
	# Extracting params

	user = params.user
	password = params.pwd
	host = params.host
	db = params.db
	table_name = params.table_name
	port = params.port
	url = params.url


	csv_name = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'

	engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

	df_iter = pd.read_csv(csv_name,iterator=True, chunksize=100000)

	df = next(df_iter)

	# Changing tpep_pickup_datetime and tpep_dropoff_datetime timestamp type
	df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
	df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)	

	# Just want to create columns with the header, not want to insert the data
	df.head(n=0).to_sql(name=table_name,con=engine,if_exists='replace')

	# Uploading data to postgres
	df.to_sql(name=table_name,con=engine,if_exists='append',method='multi')

	while True:
		t_start = time()

		df = next(df_iter)

		df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
		df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)	

		df.to_sql(name=table_name,con=engine,if_exists='append',method='multi')

		t_end = time()
		 
		print('inserted another chunk, took %.3f second' % (t_end - t_start))


#data = pd.read_csv('https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz', nrows = 100)



'''
Running in background

    docker run -it \
	-e POSTGRES_USER="root" \
	-e POSTGRES_PASSWORD="root" \
	-e POSTGRES_DB="ny_taxi_postgres_data" \
	-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgres/data \
	-p 5432:5432 \
	postgres:13

'''

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Ingest CSV data to postgres')

	parser.add_argument('--user', help='user name for postgres')
	parser.add_argument('--pwd', help='password for postgres')
	parser.add_argument('--host', help='host for postgres')
	parser.add_argument('--port', help='port for postgres')
	parser.add_argument('--db', help='database for postgres')
	parser.add_argument('--table_name', help='table name for postgres')
	parser.add_argument('--url', help='url of the csv file')

	args = parser.parse_args()
	#print(args.accumulate(args.integers))

	main(args)



'''
python upload_data.py \
	--user=root \
	--password=root \
	--host=localhost \
	--port=5432 \
	--db=ny_taxi_postgres_data \
	--table_name=yellow_taxi_data \
	--url=

'''

