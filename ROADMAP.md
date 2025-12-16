# Drive2 Development Roadmap

## ✅ Phase 1: Core Backend API (COMPLETED)

### Completed Features
- [x] Authentication system (LINE Login + JWT)
- [x] File upload and storage (MinIO)
- [x] AI processing (Gemini AI)
  - [x] Smart filename generation
  - [x] Content summarization
  - [x] Auto-tagging
  - [x] Embedding generation
- [x] File management (CRUD)
- [x] Semantic search (Qdrant)
- [x] Collections system
- [x] LINE webhook handler (basic)
- [x] Text extraction (PDF, DOCX, TXT, OCR)
- [x] Database models and migrations
- [x] Docker compose setup

---

## ✅ Phase 2.1: Celery Workers (COMPLETED - 2025-12-16)

**Goal**: Async file processing, improved performance, better user experience

### Completed Features
- [x] Celery worker setup
  - [x] Configure Celery with Redis
  - [x] Create task queue structure
  - [x] Add task retry logic
  - [x] Task status tracking
- [x] Async file processing pipeline
  - [x] Move AI processing to background
  - [x] Add progress notifications
  - [x] Batch processing support
  - [x] Failed job handling
- [x] Docker integration
  - [x] celery_worker service
  - [x] celery_beat service (periodic tasks)
  - [x] flower service (monitoring UI)

---

## 🚧 Phase 2.2: Thumbnails & Metadata (NEXT)

**Goal**: Thumbnail generation and file metadata extraction

### Features
- [ ] Thumbnail generation
  - [ ] Image thumbnails (Pillow)
  - [ ] PDF thumbnails (pdf2image)
  - [ ] Video thumbnails (ffmpeg)
  - [ ] Store thumbnails in MinIO
- [ ] File metadata extraction
  - [ ] Image EXIF data
  - [ ] PDF metadata (page count, author)
  - [ ] Video metadata (duration, resolution)
  - [ ] Document properties
- [ ] Rate limiting & quota management
  - [ ] Gemini API rate limiter
  - [ ] Daily quota tracking
  - [ ] Fallback to Ollama when quota exceeded
  - [ ] User upload limits

### Technical Details
```python
# New files to create:
- backend/app/workers/celery_app.py
- backend/app/workers/tasks/file_processing.py
- backend/app/workers/tasks/thumbnail.py
- backend/app/workers/tasks/notifications.py
- backend/app/utils/thumbnail_generator.py
- backend/app/utils/rate_limiter.py
```

---

## 🎨 Phase 3: Advanced LINE Integration

**Goal**: Rich chatbot experience, better notifications, file management via LINE

### Features
- [ ] Enhanced webhook handler
  - [ ] Download files from LINE CDN
  - [ ] Process files directly from LINE
  - [ ] Handle multiple file uploads
  - [ ] User context management
- [ ] Rich Flex Messages
  - [ ] File upload confirmation with preview
  - [ ] AI processing results (Flex Message)
  - [ ] Search results display
  - [ ] File details card
- [ ] Interactive features
  - [ ] Quick replies (rename, delete, search)
  - [ ] Postback actions
  - [ ] Rich menu design
  - [ ] Button templates
- [ ] Notifications
  - [ ] Processing complete notification
  - [ ] AI naming suggestions (approve/edit)
  - [ ] Storage quota alerts
  - [ ] Daily/weekly summaries
- [ ] LINE commands
  - [ ] `/search <query>` - Search files
  - [ ] `/list` - List recent files
  - [ ] `/stats` - Storage statistics
  - [ ] `/help` - Command help

### Technical Details
```python
# New files to create:
- backend/app/services/line_service.py
- backend/app/templates/flex_messages.py
- backend/app/utils/line_downloader.py
```

---

## 💻 Phase 4: LINE LIFF Frontend

**Goal**: Web interface for file browsing, management, and advanced features

### Features
- [ ] LIFF app setup
  - [ ] Next.js project structure
  - [ ] LIFF SDK integration
  - [ ] Authentication flow
  - [ ] API client setup
- [ ] File browser
  - [ ] Grid/List view toggle
  - [ ] Thumbnail display
  - [ ] Infinite scroll
  - [ ] Filters (date, type, tags)
  - [ ] Sorting options
- [ ] File detail page
  - [ ] File preview
  - [ ] Summary display
  - [ ] Tag management (add/remove)
  - [ ] Edit filename
  - [ ] Version history
  - [ ] Download button
- [ ] Search interface
  - [ ] Search bar with suggestions
  - [ ] Semantic search
  - [ ] Filter by tags
  - [ ] Recent searches
  - [ ] Search history
- [ ] Collections management
  - [ ] Create/edit collections
  - [ ] Add/remove files
  - [ ] Share collections
  - [ ] Collection view
- [ ] Settings & Profile
  - [ ] Storage usage stats
  - [ ] File type breakdown
  - [ ] Account settings
  - [ ] Privacy settings

### Technical Stack
```
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- LIFF SDK
- React Query (data fetching)
- Zustand (state management)
```

### Pages Structure
```
frontend/src/
├── app/
│   ├── page.tsx              # Home (file browser)
│   ├── files/[id]/page.tsx   # File detail
│   ├── search/page.tsx       # Search
│   ├── collections/page.tsx  # Collections list
│   ├── settings/page.tsx     # Settings
│   └── layout.tsx
├── components/
│   ├── FileCard.tsx
│   ├── FileGrid.tsx
│   ├── SearchBar.tsx
│   ├── CollectionCard.tsx
│   └── ...
└── lib/
    ├── api.ts
    ├── liff.ts
    └── utils.ts
```

---

## 🔒 Phase 5: Production Ready

**Goal**: Security, performance, monitoring, deployment

### Features
- [ ] Security enhancements
  - [ ] Rate limiting (per user, per IP)
  - [ ] File type validation (magic bytes)
  - [ ] Virus scanning (ClamAV)
  - [ ] SQL injection prevention
  - [ ] XSS protection
  - [ ] CSRF tokens
- [ ] Performance optimization
  - [ ] Database query optimization
  - [ ] Add database indexes
  - [ ] Redis caching strategy
  - [ ] CDN for thumbnails
  - [ ] Image optimization
  - [ ] Lazy loading
- [ ] Monitoring & Logging
  - [ ] Sentry integration (error tracking)
  - [ ] Prometheus metrics
  - [ ] Grafana dashboards
  - [ ] Log aggregation
  - [ ] Performance monitoring
- [ ] Testing
  - [ ] Unit tests (pytest)
  - [ ] Integration tests
  - [ ] API tests
  - [ ] E2E tests (Playwright)
  - [ ] Load testing
- [ ] Documentation
  - [ ] API documentation (auto-generated)
  - [ ] Architecture diagrams
  - [ ] Deployment guide
  - [ ] User manual
- [ ] Deployment
  - [ ] Docker production setup
  - [ ] CI/CD pipeline (GitHub Actions)
  - [ ] Environment management
  - [ ] Backup strategy
  - [ ] Rollback procedures

### DevOps
```yaml
# .github/workflows/ci.yml
- Lint & format check
- Run tests
- Build Docker images
- Security scan
- Deploy to staging
- Deploy to production
```

---

## 🚀 Phase 6: Advanced Features

**Goal**: AI improvements, collaboration, analytics

### Features
- [ ] Advanced AI features
  - [ ] Multi-language support (OCR)
  - [ ] Smart file categorization
  - [ ] Duplicate detection (similar content)
  - [ ] Content suggestions
  - [ ] Auto-organize by topic
- [ ] Collaboration
  - [ ] Share files with other users
  - [ ] Collection permissions (view/edit)
  - [ ] Comments on files
  - [ ] Activity feed
  - [ ] Team workspaces
- [ ] Analytics & Insights
  - [ ] Storage trends
  - [ ] Most accessed files
  - [ ] Search analytics
  - [ ] AI accuracy metrics
  - [ ] User behavior insights
- [ ] File operations
  - [ ] Batch operations (delete, move, tag)
  - [ ] File compression
  - [ ] File conversion (PDF to images, etc.)
  - [ ] Merge PDFs
  - [ ] Extract pages
- [ ] AI improvements
  - [ ] Custom AI models (fine-tuned)
  - [ ] Better summarization
  - [ ] Question answering on documents
  - [ ] Chat with your files (RAG)

---

## 📊 Priority Matrix

### High Priority (Must Have)
1. ✅ Phase 1: Core Backend API
2. 🚧 Phase 2: Background Processing
3. 🚧 Phase 3: Advanced LINE Integration

### Medium Priority (Should Have)
4. Phase 4: LINE LIFF Frontend
5. Phase 5: Production Ready

### Low Priority (Nice to Have)
6. Phase 6: Advanced Features

---

## 🎯 Next Immediate Steps

### Phase 2.1 - Celery Workers (Week 1)
1. Setup Celery with Redis
2. Create file processing tasks
3. Move AI processing to background
4. Add progress tracking

### Phase 2.2 - Thumbnails & Metadata (Week 2)
1. Implement thumbnail generation
2. Extract file metadata
3. Store in database and MinIO
4. Add to API responses

### Phase 3.1 - Enhanced LINE Webhook (Week 3)
1. Download files from LINE CDN
2. Process files from LINE messages
3. Send Flex Message notifications
4. Add quick reply actions

### Phase 3.2 - Rich Notifications (Week 4)
1. Design Flex Message templates
2. Send processing complete notifications
3. Interactive file cards
4. Rich menu setup

---

## 🔄 Continuous Improvements

Throughout all phases:
- Performance optimization
- Bug fixes
- Security updates
- User feedback integration
- Documentation updates
- Code refactoring

---

## 📝 Notes

### Technology Decisions
- **Why Celery?** - Mature, reliable, Python native
- **Why Qdrant?** - Fast, open-source, good Python support
- **Why Gemini Free Tier?** - 1500 req/day is enough for MVP
- **Why LIFF?** - Native LINE integration, no app install needed

### Potential Challenges
- Gemini API rate limits (15 RPM, 1500/day)
- MinIO external server latency
- Large file processing time
- OCR accuracy for Thai language
- LINE webhook timeout (30 seconds)

### Fallback Strategies
- Use Ollama for AI when Gemini quota exceeded
- Queue processing for large files
- Respond quickly to LINE, process async
- Cache thumbnails aggressively

---

Last Updated: 2025-12-12
