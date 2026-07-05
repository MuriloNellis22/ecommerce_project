import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# Exportação de dados vindos de um arquivo CSV.
def extract():

    df = pd.read_csv(
    "../data/raw/OnlineRetail.csv",
    encoding="latin1"
)
    return df

print('Extraindo dados...')

# Transformação de dados para remoção de duplicatas e valores nulos nas tabelas mencionadas.
def transform(df):

    df = df.drop_duplicates()
    df = df.dropna(
    subset=[
        "CustomerID",
        "InvoiceDate",
        "Quantity",
        "UnitPrice"
    ]
)
    
    df_limpo = df[df['Quantity'] > 0 ].copy()
    df_limpo = df_limpo[df_limpo['UnitPrice'] > 0].copy()
    df_limpo['Revenue'] = df_limpo['Quantity'] * df_limpo['UnitPrice']

    return df_limpo

print('Transformando dados...')


# Criando tabelas as tabelas dimensionais para clientes, produtos e vendas.
def create_dimensions(df_limpo):

    df_limpo['InvoiceDate'] = pd.to_datetime(df_limpo['InvoiceDate'])
    df_limpo['Year'] = df_limpo['InvoiceDate'].dt.year
    df_limpo['Month'] = df_limpo['InvoiceDate'].dt.month
    df_limpo['Day'] = df_limpo['InvoiceDate'].dt.day
    df_limpo['Hour'] = df_limpo['InvoiceDate'].dt.hour
    df_limpo = df_limpo.drop(columns=['InvoiceDate'])

    dim_clientes = (
    df_limpo[["CustomerID", "Country"]].drop_duplicates()
)
    
    dim_produtos = (
    df_limpo[["StockCode", "Description"]].drop_duplicates()
)
    
    fato_vendas = (
    df_limpo[
        [
            "InvoiceNo",
            "CustomerID",
            "StockCode",
            "Quantity",
            "UnitPrice",
            "Revenue",
            "Year",
            "Month",
            "Day",
            "Hour"
        ]
    ]
)
    return dim_clientes, dim_produtos, fato_vendas

print('Criando dimensões...')

# Carregando as tabelas para o banco ecommerce_dw no PostgreSQL.
def load_postgres(engine, dim_clientes, dim_produtos, fato_vendas):

    dim_clientes.to_sql(
    'dim_clientes',
    engine,
    if_exists='replace',
    index=False
)
    
    dim_produtos.to_sql(
    'dim_produtos',
    engine,
    if_exists='replace',
    index=False
)
    
    fato_vendas.to_sql(
    'fato_vendas',
    engine,
    if_exists='replace',
    index=False
)
    
    print('Carregando PostgreSQL...')


# Realizando as exportações das tabelas para arquivo parquet.
def export_parquet(dim_clientes, dim_produtos, fato_vendas):

    dim_clientes.to_parquet('../data/processed/dim_clientes.parquet', engine='pyarrow', index=False)
    dim_produtos.to_parquet('../data/processed/dim_produtos.parquet', engine='pyarrow', index=False)
    fato_vendas.to_parquet('../data/processed/fato_vendas.parquet', engine='pyarrow', index=False)

    print('Exportando para arquivo parquet...')


# Executando pipeline.
def main():

    df = extract()

    df_limpo = transform(df)

    dim_clientes, dim_produtos, fato_vendas = create_dimensions(df_limpo)

    engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

    load_postgres(
        engine,
        dim_clientes,
        dim_produtos,
        fato_vendas
    )

    export_parquet(
        dim_clientes,
        dim_produtos,
        fato_vendas
    )

    print('Pipeline finalizado com sucesso!')

if __name__ == "__main__":
    main()