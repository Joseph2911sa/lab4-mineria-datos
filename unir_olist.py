"""
Une los CSV originales de Olist en un solo archivo plano: olist_ventas.csv
Una fila = un item vendido (112,650 filas).

Uso:  python unir_olist.py C:\\database\\olist_ecommerce
"""
import os
import sys
import pandas as pd

carpeta = sys.argv[1] if len(sys.argv) > 1 else "."
leer = lambda nombre: pd.read_csv(os.path.join(carpeta, nombre))

items = leer("olist_order_items_dataset.csv")
ordenes = leer("olist_orders_dataset.csv")
productos = leer("olist_products_dataset.csv")
traduccion = leer("product_category_name_translation.csv")
clientes = leer("olist_customers_dataset.csv")
vendedores = leer("olist_sellers_dataset.csv")
resenas = leer("olist_order_reviews_dataset.csv")
pagos = leer("olist_order_payments_dataset.csv")

# Una orden puede tener varias resenas: se conserva la mas reciente.
resenas = (resenas.sort_values("review_answer_timestamp")
           .drop_duplicates("order_id", keep="last")[["order_id", "review_score"]])

# Una orden puede tener varios pagos: se resume en una fila por orden.
pagos = (pagos.sort_values("payment_sequential").groupby("order_id")
         .agg(payment_type=("payment_type", "first"),
              payment_installments=("payment_installments", "max"),
              payment_value=("payment_value", "sum"))
         .reset_index())

df = (items
      .merge(ordenes, on="order_id", how="left")
      .merge(productos, on="product_id", how="left")
      .merge(traduccion, on="product_category_name", how="left")
      .merge(clientes, on="customer_id", how="left")
      .merge(vendedores, on="seller_id", how="left")
      .merge(resenas, on="order_id", how="left")
      .merge(pagos, on="order_id", how="left"))

# Se quitan identificadores tipo hash (no aportan al EDA y pesan mucho)
# y fechas intermedias que no se analizan.
df = df.drop(columns=["order_id", "product_id", "seller_id", "customer_id",
                      "customer_unique_id", "product_category_name",
                      "shipping_limit_date", "order_approved_at",
                      "order_delivered_carrier_date"])

df.to_csv("olist_ventas.csv", index=False)
print("Listo:", df.shape, "-> olist_ventas.csv")
