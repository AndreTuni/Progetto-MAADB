get 20 random emails
```mongosh
db.person.aggregate([
  { $sample: { size: 50 } }, // Sample more documents to have enough emails
  { $unwind: "$email" },     // Flatten the email array
  { $sample: { size: 20 } }, // Sample 20 random email addresses
  { $project: { _id: 0, email: 1 } }
]);
```

## results
Yang141@gmail.com
David21990232571293@yahoo.com
Mpeti13194139562981@zoho.com
Jie32985348897478@yahoo.com
Ahmed32985348853640@zoho.com
Francis30786325595172@gmail.com
Louisa17592186063059@mascara.ws
Mpeti13194139562981@gmx.com
Wolfgang4283@gmail.com
Yang8796093083418@yahoo.com
Cleopa35184372095654@hotmail.com
Pablo24189255877730@gmail.com
Cleopa35184372095654@gmx.com
Mpeti13194139562981@yahoo.com
Pol15393162814714@yahoo.com
Jie32985348897478@gmail.com
Lin28587302387164@gmx.com


### TODO:
- Mostra i post creati da una persona 
- Trova tutte le persone che lavorano nella stessa azienda da un determinato anno e sono membri dello stesso forum
- Trova i tag più usati da persone nate nella stessa città di un utente dato