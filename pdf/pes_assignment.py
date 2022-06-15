import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymysql

# Replace username, password, dbname & host with appropriate credentials
connection = pymysql.connect(user='root', password='passwd', database='ord_mgmt', host='localhost')

try:
    sql_qry = "select year(order_date) as year, month(order_date) as month, i.product_id, \
                sum(ordered_qty) as tot_qty, sum(product_price * ordered_qty) as tot_sales \
                from order_header h, order_items i, product p \
                where h.order_id = i.order_id \
                and i.product_id = p.product_id \
                group by year, month, product_id order by 1;"

    sql_output = pd.read_sql_query(sql_qry, connection)   # Execute the query & get its output
    sqldf = pd.DataFrame(sql_output, columns=['year', 'month', 'product_id', 'tot_qty', 'tot_sales'])
    print(sqldf)

    grpby_column = 'year'
    sqldf_grpby = sqldf.groupby(grpby_column).aggregate(np.sum)
    plt.figure(figsize=(20,6))

    x_values = np.array(sqldf_grpby['month'].keys())
    y_values = np.array((sqldf_grpby['tot_sales']))
    plt.title('Year Sales Report')
    plt.xlabel(grpby_column)
    plt.ylabel('Sales amt')
    plt.xticks(x_values)
    plt.plot(x_values, y_values)
    plt.bar(x_values, y_values)
    plt.xticks(fontsize=8)

    for a, b in zip(x_values, y_values):  # Printing values
        plt.text(a, b, int(b))
    plt.grid(True)
    plt.show()

finally:
    connection.close()
