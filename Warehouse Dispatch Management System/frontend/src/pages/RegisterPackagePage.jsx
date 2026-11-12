import {useState, useEffect} from 'react';
import {Link }  from 'react-router';


function BrowsePage() {
    const [products, setProducts] = useState([]);
    const [page, setPage] = useState(1);

    useEffect(() => {
        async function loadProducts() {
            const res = await fetch("http://localhost:8001/packages");
            const data = await res.json();

            setProducts(data.products);
        }
        loadProducts();
    }, [page]);