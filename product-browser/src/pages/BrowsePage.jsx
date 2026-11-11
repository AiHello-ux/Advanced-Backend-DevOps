import { useState, useEffect } from 'react'
import {Link } from 'react-router-dom'

// pagination means limit how much should show 

export default function BrowsePage() {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);

  useEffect(() => {
    async function loadProducts() {
      const skip = (page - 1) * 10;
      const res = await fetch(`https://dummyjson.com/products?limit=10&skip=${skip}`);
      const data = await res.json();
      setProducts(data.products);
    }
    loadProducts();
  }, [page]);

  return (
    <>
      <button disabled={page === 1} onClick={() => setPage(page -1)}> Previous </button>
      <button disabled={page === products.length} onClick={() => setPage(page +1)}> Next </button>

      <span>Page {page}</span>
      <p>loaded products are {products.length}</p>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <img src={product.thumbnail}/>
            <p>Title: {product.title}</p>
            <p>Price: ${product.price}</p>
            <p>rating: {product.rating}</p>
            <p>Category: {product.category}</p>
            <Link to={`/product/${product.id}`}>View Details</Link>
          </li>
        ))}
      </ul>
    </>
  );
}