# SmartShop - Vercel Deployment

## Quick Start

This project is configured for deployment on Vercel.

### Backend API
- FastAPI application deployed as serverless functions
- Uses `requirements-vercel.txt` for dependencies
- Configured with `vercel.json`

### Frontend
- React/Vite application
- Configured with `frontend/vercel.json`
- Builds to `dist` directory

## Deployment

1. **Deploy Backend**: Use the root directory
2. **Deploy Frontend**: Use the `frontend` directory
3. **Set Environment Variables**: Configure in Vercel dashboard

## Important Notes

- Uses mock scrapers (no browser automation)
- MongoDB connection is optional
- Optimized for serverless environment

See `VERCEL_DEPLOYMENT.md` for detailed instructions.
