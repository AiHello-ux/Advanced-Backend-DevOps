import React, { useState, useEffect } from "react";

export default function ProductsPage() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    async function loadProducts() {
      const res = await fetch("https://dummyjson.com/products");
      const data = await res.json();
      setProducts(data.products);
    }
    loadProducts();
  }, []);

  return (
    <>
      <p>number of loaded products are {products.length}</p>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <img src={product.thumbnail} />
            <p>Title:{product.title} </p>
            <p>Price: ${product.price}</p>
            <p>rating:{product.rating}</p>
            <p>Category: {product.category}</p>
            <p>{product.reviews.length} reviews</p>
          </li>
        ))}
      </ul>
    </>
  );
}