import { defineConfig } from 'vite'
import type { ViteDevServer } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { IncomingMessage, ServerResponse } from 'http'

// Vite plugin to read/write .kibo files directly for local dev cockpit
const kiboDevApi = () => ({
  name: 'kibo-dev-api',
  configureServer(server: ViteDevServer) {
    server.middlewares.use((req: IncomingMessage, res: ServerResponse, next: () => void) => {
      if (req.url?.startsWith('/api/kibo')) {
        const urlParams = new URL(req.url, 'http://localhost')
        const filepath = urlParams.searchParams.get('path')
        if (!filepath) {
          res.statusCode = 400
          return res.end('Path parameter is required')
        }
        
        // Ensure path stays inside Kibo workspace
        const resolvedPath = path.resolve('/Users/iceman/Documents/Code/Kibo', filepath)
        if (!resolvedPath.startsWith('/Users/iceman/Documents/Code/Kibo')) {
          res.statusCode = 403
          return res.end('Access Denied')
        }
        
        if (req.method === 'GET') {
          if (!fs.existsSync(resolvedPath)) {
            res.statusCode = 404
            res.setHeader('Content-Type', 'application/json')
            return res.end(JSON.stringify({ error: 'File not found' }))
          }
          if (fs.lstatSync(resolvedPath).isDirectory()) {
            const files = fs.readdirSync(resolvedPath)
            res.setHeader('Content-Type', 'application/json')
            return res.end(JSON.stringify({ isDirectory: true, files }))
          }
          const content = fs.readFileSync(resolvedPath, 'utf8')
          res.setHeader('Content-Type', 'application/json')
          return res.end(JSON.stringify({ content }))
        } else if (req.method === 'POST') {
          let body = ''
          req.on('data', chunk => { body += chunk })
          req.on('end', () => {
            try {
              const payload = JSON.parse(body)
              fs.writeFileSync(resolvedPath, payload.content, 'utf8')
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ success: true }))
            } catch (e) {
              res.statusCode = 500
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ error: (e as Error).message }))
            }
          })
          return
        }
      }
      next()
    })
  }
})

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), kiboDevApi()],
  server: {
    port: 5173,
    host: '127.0.0.1',
    cors: {
      origin: ['http://127.0.0.1:5173', 'http://localhost:5173'],
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
      credentials: true
    },
    headers: {
      'Access-Control-Allow-Origin': 'http://127.0.0.1:5173',
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Content-Security-Policy': "default-src 'self' 'unsafe-inline' 'unsafe-eval' data:; connect-src 'self' http://127.0.0.1:* http://localhost:* ws://127.0.0.1:* ws://localhost:*;"
    }
  }
})
