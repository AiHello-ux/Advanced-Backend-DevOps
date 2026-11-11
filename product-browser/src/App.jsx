import { useState } from 'react'
import ProductsPage from './pages/ProductsPage'
import { Routes, Route, Link } from 'react-router-dom'
import BrowsePage from './pages/BrowsePage'
import ProductDetailPage from './pages/ProductDetailPage'
// route the route for each page 
// and everything will wrape around the route
// instead of reloading the page it goes directly to the page 
// route for that address  which page to render 
// link help to changes pages instead of reloading it 
//* means anything apart from what is defined in the route will be redirected to the home page for example if i add 23edc instead of / it will show the error 404 which message we wrote


export default function App() {
  return (
    <>
    <nav>
      <Link to="/">All Products</Link> 
      <Link to="/browse">Browse</Link>
    </nav>
    <Routes>
      <Route path="/" element={<ProductsPage />} />
      <Route path="/browse" element={<BrowsePage />} />
      <Route path="/product/:id" element={<ProductDetailPage />} />
      <Route path="*" element={<ProductsPage />} />
    </Routes>
    </>
  );
}