import {useParams} from 'react-router-dom'
import {Link} from 'react-router-dom'
import { useState, useEffect } from 'react'

export default function ProductDetailPage() {
  const {id} = useParams()
  const [product, setProduct] = useState(null);

  useEffect(() => {
    async function loadProduct() {
      const res = await fetch(`https://dummyjson.com/products/${id}`);
      const data = await res.json();
      setProduct(data);
    }
    loadProduct();
  }, [id]);
  if (!product){
    return <p>Loading...</p>;
  }
  return (
    <div>
      <h2>{product.title}</h2>
      <img src={product.thumbnail} alt={product.title} />
      <p>Description: {product.description}</p>
      <p>Price: ${product.price}</p>
      <p>Category: {product.category}</p>
      <p>Rating: {product.rating}</p>
      <p>Stock: {product.stock}</p>
      <h3>Images</h3>
      <ul>
        {product.images && product.images.map((image, index) => (
          <li key={index}>
            <img src={image} />
          </li>
        ))}
      </ul>

      <h3>Reviews</h3>
      <ul>
        {product.reviews && product.reviews.map((review, index) =>d (
          <li key={index}>
            <p><strong>{review.reviewerName}</strong> ({review.reviewerEmail})</p>
            <p>Rating: {review.rating}/5</p>
            <p>{review.comment}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}