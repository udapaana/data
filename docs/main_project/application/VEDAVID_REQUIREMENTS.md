# VedaVid Requirements Document

## Project Overview
VedaVid is a modern web application for Vedic adhyayana (study/recitation), providing a clean interface to study texts from multiple śākhās with focus on traditional learning methods.

## Core Objective
Create a distraction-free study platform for serious practitioners of Vedic recitation, supporting multiple śākhās and all text types (Saṃhitā, Brāhmaṇa, Āraṇyaka).

## Functional Requirements

### 1. Text Display for Adhyayana

#### 1.1 Multi-Śākhā Navigation
- **Veda Selection**: All four Vedas from unified corpus
  - Ṛgveda
  - Sāmaveda  
  - Yajurveda (Kṛṣṇa & Śukla)
  - Atharvaveda
- **Śākhā Selection**: Available śākhās per Veda
  - Taittirīya (complete - 4,903 texts)
  - Other śākhās from unified corpus
- **Text Types**: All three types in Phase 1
  - Saṃhitā (verses with pada/saṃhitā)
  - Brāhmaṇa (prose sections)
  - Āraṇyaka (forest texts)

#### 1.2 Hierarchical Navigation
- **Preserve Native Structure**: Each śākhā maintains its traditional organization
  - Ṛgveda: Maṇḍala → Sūkta → Ṛk
  - Taittirīya: Kāṇḍa → Prapāṭhaka → Anuvāka → Verse
  - Śukla Yajurveda: Adhyāya → Verse
  - Each śākhā's unique divisions respected
- **Dynamic Navigation**: UI adapts to each text's structure
- **Current Location**: Breadcrumbs reflect actual hierarchy
- **Quick Jump**: Context-aware navigation per śākhā

#### 1.3 Reading Modes for Study
- **Pada-Saṃhitā View**: Side-by-side for Saṃhitā texts
- **Prose View**: Clean layout for Brāhmaṇa/Āraṇyaka
- **Focus Mode**: Single verse/section at a time
- **Continuous Mode**: Smooth scrolling through sections

#### 1.4 Essential Display Settings
- **Font Size**: Large/Medium/Small presets
- **Line Spacing**: Comfortable reading
- **Script Selection**:
  - Devanagari (primary)
  - IAST
  - Harvard-Kyoto
  - Regional scripts (Tamil, Telugu, etc.)

### 2. Study Tools (Adhyayana-focused)

#### 2.1 Navigation for Practice
- **Next/Previous**: Quick verse navigation
- **Jump to Verse**: Direct input (e.g., "1.2.3.4")
- **Section Completion**: Mark sections as studied
- **Resume**: Remember last position

#### 2.2 Recitation Support
- **Highlight Current**: Visual indicator for current verse
- **Hide/Show**: Toggle pada or saṃhitā for memorization
- **Print View**: Clean format for offline study
- **Full Screen**: Distraction-free mode

#### 2.3 Search for Reference
- **Simple Search**: Find verses quickly
- **Search Scope**: Current text or all texts
- **Go to Result**: Direct navigation from results

### 3. Mobile-First Design

#### 3.1 Touch Optimization
- **Large Touch Targets**: Easy navigation
- **Swipe Gestures**: Next/previous verse
- **Pinch Zoom**: Text size adjustment
- **Stable Layout**: No jumping during load

#### 3.2 Offline Support
- **Progressive Web App**: Installable
- **Offline Caching**: Study without internet
- **Sync Progress**: When back online

## Technical Requirements

### 1. Architecture (Simplified)

#### 1.1 Frontend Stack
- **Framework**: Vue 3 with Composition API
- **Language**: TypeScript
- **State**: Pinia for settings/progress
- **Routing**: Vue Router for deep links
- **Styling**: Tailwind CSS

#### 1.2 Data Architecture
- **Primary**: SQLite database via SQL.js
- **Fallback**: JSON chunks for static hosting
- **Caching**: Local storage for offline

### 2. Performance Targets
- **Initial Load**: < 3 seconds
- **Text Navigation**: Instant (< 100ms)
- **Search**: < 500ms
- **Smooth Scrolling**: No jank

### 3. Essential Features Only
- **No Authentication**: Public access
- **No User Accounts**: Local storage only
- **No Social Features**: Pure study tool
- **No Ads/Tracking**: Privacy-first

## Data Requirements

### 1. Unified Corpus Support
- Load from SQLite database with all śākhās
- Support batch loading for performance
- Respect each śākhā's unique structure
- No forced uniformity - display as organized in source
- Dynamic UI components that adapt to text structure

### 2. Text Structure
```typescript
interface VedicText {
  id: string;
  veda: string;
  sakha: string;
  textType: 'samhita' | 'brahmana' | 'aranyaka';
  location: {
    // Flexible structure - use what exists in the source
    mandala?: number;      // For Ṛgveda
    kanda?: number;        // For Taittirīya
    adhyaya?: number;      // For Śukla Yajurveda
    sukta?: number;        // For Ṛgveda, Sāmaveda
    prapathaka?: number;   // For Taittirīya
    anuvaka?: number;      // For various texts
    verse?: number;        // Universal
    section?: string;      // For prose texts
    // ... any other native divisions
  };
  content: {
    samhita?: string;
    pada?: string;
    primary?: string;  // For prose texts
  };
}
```

## Implementation Priorities

### Phase 1: Complete Adhyayana Platform (MVP)
1. **Multi-śākhā Support**: Display all available texts
2. **All Text Types**: Saṃhitā, Brāhmaṇa, Āraṇyaka
3. **Core Navigation**: Hierarchical browse + search
4. **Reading Modes**: Pada-Saṃhitā, prose, focus mode
5. **Mobile Responsive**: Touch-friendly interface
6. **Script Switching**: Devanagari + transliterations
7. **Offline Support**: PWA with caching
8. **Progress Tracking**: Remember position

### Phase 2: Enhanced Study Tools
1. **Advanced Search**: Filters and regex
2. **Bookmarks**: Save important verses
3. **Export**: PDF/text generation
4. **Keyboard Shortcuts**: Power user features
5. **Custom Themes**: More visual options

### Phase 3: Future Enhancements
1. **Audio Support**: Pronunciation guides
2. **Variant Display**: Regional differences
3. **Cross-references**: Related passages
4. **Commentary**: Traditional explanations

## Design Principles
1. **Clarity**: Clean, readable interface
2. **Speed**: Instant response to actions
3. **Focus**: No distractions from study
4. **Tradition**: Preserve each śākhā's authentic structure
5. **Flexibility**: UI adapts to different organizational patterns
6. **Accessibility**: Works for all users

## Success Metrics
- **Load Time**: < 3s on 3G mobile
- **Navigation**: < 100ms response
- **Mobile Usage**: Fully functional on phones
- **Offline**: 100% functionality without internet
- **Text Accuracy**: Zero rendering errors

---

*This document focuses on creating the best possible adhyayana experience with the complete unified corpus as the foundation.*