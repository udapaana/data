# Vedic Transliteration Schemes

This document defines ASCII-based transliteration schemes for each Vedic śākhā, based on actual source data patterns.

## Common Base (All Śākhās)

### Basic Characters (SLP1-based)
```
# Vowels
a A i I u U f F x X e E o O

# Consonants
k K g G N    # velars
c C j J Y    # palatals  
w W q Q R    # retroflexes
t T d D n    # dentals
p P b B m    # labials

# Semivowels & Others
y r l v
S z s h
M H          # anusvara, visarga
L            # vedic l
```

### Common Punctuation
```
|     # minor pause (word/pada boundary)
||    # major pause (half-verse)
|||   # full stop (verse end)
.     # sentence end
,     # list separator
```

## Taittirīya Śākhā (Yajurveda)

Based on VedaVMS (Baraha) and Vedanidhi sources.

### Accent Marks
```
# Primary accents (after syllable)
\     # udātta (high tone)
_     # anudātta (low tone)  
=     # svarita (falling tone)

# Examples:
agni\m I_Le_ puro_hita\m
va\yu_H kze_piSTHA\ deva\tA
```

### Special Features
```
&     # avagraha (elision mark)
*     # halanta (virama)
~     # nasalization marker

# Anusvara variations
M     # standard anusvara
M~    # nasalized anusvara

# Inline phonetic annotations (preserved from Baraha)
(gm)  # guttural + m sound (ṅ-like nasal)
(gg)  # guttural + g sound (ṅ before g/k)
# These resemble the actual sounds: g+m, g+g
```

## Śākala Śākhā (Ṛgveda)

Based on Vedanidhi source.

### Accent Marks
```
# Same as Taittirīya
\     # udātta
_     # anudātta
=     # svarita (when marked)

# Example:
a\gni_mI\Le puro\hita_m
```

### Special Features (Phonetically Intuitive)
```
# Sound variations
~     # wave = prolonged sound
(n)   # nasalization marker

# Visarga variations (context-based)
HK    # H before k/kh (sounds like K)
HP    # H before p/ph (sounds like P)  
Hr    # H before vowels (sounds like r)

# Minimal marking philosophy
# Svarita often unmarked (contextual)
```

## Kauthuma Śākhā (Sāmaveda)

Based on Vedanidhi source with musical notations.

### Accent Marks
```
# Basic accents
\     # udātta
_     # anudātta
=     # svarita

# Musical extensions (numbers = mātrā count)
2     # 2 mātrās (intuitive timing)
3     # 3 mātrās
4     # 4 mātrās
5     # 5 mātrās
```

### Musical Notations (Phonetically Intuitive)
```
^     # up arrow = lift/pause
~     # wave = voice vibration/kampita
,     # comma = natural breath pause
-     # dash = smooth connection

# Stobha elements (actual sounds)
(ho)  (ha)  (hum)  (i)  (e)  # parentheses = inserted sounds

# Example:
a\gna3 A_ yA_hi vI_taye^
a\gna (ho) A_ yA_hi vI_taye^
```

### Numerical Notations (Saptasvara)
```
1=sa  2=re  3=ga  4=ma  5=pa  6=dha  7=ni
Combined: 234 = re-ga-ma (ascending pattern)
```

## Śaunaka Śākhā (Atharvaveda)

Based on Vedanidhi source.

### Accent Marks
```
# Same basic system
\     # udātta
_     # anudātta
=     # svarita

# Example:
ve\na_s ta\t pa\Sya_t para\mam
```

### Special Features (Phonetically Intuitive)
```
# Ritual/magical emphasis
!     # exclamation = loud/emphatic
%     # percent = partial/whispered voice

# Nasal variations (sound-based)
(nk)  # n + k sound (like "bank")
(ng)  # n + g sound (like "sing")
(nc)  # n + c sound (like "pinch")
(nt)  # n + t sound (like "want")
```

## Conversion Rules

### From Source to Scheme

1. **VedaVMS Baraha → Scheme**:
   - `#` → `\` (udātta)
   - `q` → `_` (anudātta)
   - Complex marks simplified

2. **Vedanidhi Devanagari → Scheme**:
   - `.` → `\` (udātta)
   - `ˆ` → `_` (anudātta)
   - Preserve special marks

### Validation Rules

1. **Accent placement**: Always after the syllable
2. **No double accents**: One accent per syllable
3. **Stobha marking**: Always in `{}`
4. **Musical notes**: Clear separation from text

## Examples by Śākhā

### Taittirīya (with phonetic annotations)
```
Source (Baraha): iqShE tvAq | UqrjE tvAq
Scheme:          i_SE tvA_ | U_rjE tvA_

Source (Baraha): aqGaSa(gm)#saq | dRu(gm)ha#sva
Scheme:          a_GaSa(gm)\sa_ | dRu(gm)ha\sva
                 # (gm) = guttural+m sound preserved

Source (Vedanidhi): वायु.र्वै क्षेपिष्ठा
Scheme:             vA\yu_rvai kze\piSTHA_
```

### Ṛgveda (minimal, context-aware)
```
Source: अग्निमीळे पुरोहितम्
Scheme: agni\mI_Le puro\hita_m

With visarga variation: namaH pAhi → namaHP pAhi
                       # HP = H sounds like P before p
```

### Sāmaveda (musical timing)
```
Source: अग्न आ याहि वीतये
Scheme: a\gna3 A_ yA_hi vI_taye^
        # 3 = 3 mātrās elongation

With stobha: a\gna (ho) A_ yA_hi (hum) vI_taye^
             # (ho), (hum) = actual sounds inserted

Complex: औहोइहुवा3होइ → (auho)(i)(huvA)3(hoi)
         # Each sound element clearly marked
```

### Atharvaveda (ritual emphasis)
```
Source: वेन.स्त.त्पश्य.त्परम.ङ्गुहा  
Scheme: ve\na_s ta\t pa\Sya_t para\mam guhA\

With emphasis: mRtyo! mA → mRtyo! mA
               # ! = ritual emphasis

With nasal: सङ्कल्प → sa(nk)alpa  
            # (nk) = n+k sound cluster
```

## Implementation Notes

1. **Parser modularity**: Each śākhā gets its own parser module
2. **Common base**: Shared character mappings across all
3. **Validation**: Śākhā-specific rules enforced
4. **Round-trip**: Must preserve all accent information
5. **ASCII-safe**: No Unicode in scheme representation