when HTTP_REQUEST {
   HTTP::respond 200 content {
      <html>
         <head>
            <title>Responder Page</title>
         </head>
         <body>
            Responder Page.
         </body>
      </html>
   }
}
