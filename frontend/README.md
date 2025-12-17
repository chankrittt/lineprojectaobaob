# Drive2 LIFF Frontend

LINE LIFF frontend application for Drive2 - AI-Powered File Management System.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **LIFF SDK** - LINE integration
- **React Query** - Data fetching and caching
- **Zustand** - State management
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- LINE LIFF app (create at LINE Developers Console)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create `.env.local`:

```bash
cp .env.local.example .env.local
```

3. Configure environment variables:

```env
NEXT_PUBLIC_LIFF_ID=your-liff-id
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

4. Run development server:

```bash
npm run dev
```

5. Open LIFF app in LINE:
   - Must be opened from LINE app
   - Use LIFF URL: `https://liff.line.me/{LIFF_ID}`

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── page.tsx         # Home (auth redirect)
│   │   ├── files/           # File browser
│   │   ├── search/          # Search page
│   │   ├── collections/     # Collections
│   │   └── settings/        # Settings
│   ├── components/          # React components
│   │   ├── ui/              # Base UI components
│   │   ├── files/           # File-related components
│   │   ├── search/          # Search components
│   │   └── collections/     # Collection components
│   └── lib/                 # Utilities
│       ├── api-client.ts    # API client
│       ├── types.ts         # TypeScript types
│       └── utils.ts         # Helper functions
├── public/                  # Static assets
└── package.json
```

## Features

### ✅ Implemented

- **LIFF Authentication** - Auto login with LINE
- **File Browser** - Grid/List view toggle
- **File Detail** - Preview, summary, tags, metadata
- **Search** - Full-text and semantic search
- **Collections** - Organize files
- **Settings** - Storage stats, account info

### 🚧 In Progress

- File upload UI
- Thumbnail display
- Tag management
- Sharing features

### 📋 Planned

- Rich file preview (PDF, images, videos)
- Advanced filters
- Activity feed
- Collaborative features

## Development

### Build for production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project to Vercel
3. Configure environment variables
4. Deploy

### Manual Deployment

```bash
npm run build
# Deploy the `.next` folder to your server
```

## LIFF Configuration

1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create or select your provider
3. Create LIFF app
4. Configure:
   - **Endpoint URL**: Your app URL
   - **Scope**: `profile`, `openid`
   - **Bot Link Feature**: Optional

## API Integration

The app communicates with the Drive2 backend API:

- **Base URL**: Configured in `NEXT_PUBLIC_API_URL`
- **Authentication**: JWT tokens from LINE login
- **Endpoints**: See `src/lib/api-client.ts`

## Troubleshooting

### LIFF not initializing

- Check LIFF ID is correct
- Ensure app is opened from LINE app
- Check browser console for errors

### API requests failing

- Verify backend is running
- Check API URL in `.env.local`
- Check CORS configuration on backend
- Verify authentication token

### Build errors

- Clear `.next` folder: `rm -rf .next`
- Clear node_modules: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npx tsc --noEmit`

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [LIFF Documentation](https://developers.line.biz/en/docs/liff/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)

## License

Proprietary - All rights reserved

---

Built with ❤️ using Next.js and LINE LIFF
