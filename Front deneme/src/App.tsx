import { useState, useMemo, useEffect } from 'react';
import { Search, ArrowUpDown, MapPin, Star, BookOpen, Users, Trophy, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface University {
  id: number;
  name: string;
  city: string;
  successScore: number;
  publicationScore: number;
  studentSatisfaction: number;
  overallScore: number;
  ranking: number;
  year: number;
}

// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// API functions
async function fetchUniversities(year: number = 2022): Promise<University[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/universities/`);
    if (!response.ok) {
      throw new Error('Failed to fetch universities');
    }
    const data = await response.json();
    
    return data.universities
      .filter((uni: any) => uni.scores[year]?.ortalama !== null)
      .map((uni: any, index: number) => {
        const latestScore = uni.scores[year];
        return {
          id: index + 1,
          name: uni.name,
          city: extractCityFromName(uni.name),
          successScore: Math.round((latestScore?.ortalama || 0) * 100),
          publicationScore: Math.round((latestScore?.medyan || 0) * 100),
          studentSatisfaction: Math.round((latestScore?.ortalama || 0) * 100),
          overallScore: Math.round((latestScore?.ortalama || 0) * 100),
          ranking: index + 1, // Will be sorted later
          year: year
        };
      })
      .sort((a: University, b: University) => b.overallScore - a.overallScore)
      .map((uni: University, index: number) => ({
        ...uni,
        ranking: index + 1
      }));
  } catch (error) {
    console.error('Error fetching universities:', error);
    return [];
  }
}

async function fetchAvailableYears(): Promise<number[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/universities/`);
    if (!response.ok) {
      throw new Error('Failed to fetch universities');
    }
    const data = await response.json();
    
    // Extract all available years from the data
    const years = new Set<number>();
    data.universities.forEach((uni: any) => {
      Object.keys(uni.scores).forEach(year => {
        if (uni.scores[year]?.ortalama !== null) {
          years.add(parseInt(year));
        }
      });
    });
    
    return Array.from(years).sort((a, b) => b - a); // Sort descending
  } catch (error) {
    console.error('Error fetching available years:', error);
    return [2022]; // Fallback to 2022
  }
}

function extractCityFromName(name: string): string {
  // Extract city from university name
  const cityMap: { [key: string]: string } = {
    'İSTANBUL': 'İstanbul',
    'ANKARA': 'Ankara',
    'İZMİR': 'İzmir',
    'BURSA': 'Bursa',
    'ANTALYA': 'Antalya',
    'ADANA': 'Adana',
    'KONYA': 'Konya',
    'GAZİANTEP': 'Gaziantep',
    'MERSİN': 'Mersin',
    'DİYARBAKIR': 'Diyarbakır',
    'KAYSERİ': 'Kayseri',
    'ESKİŞEHİR': 'Eskişehir',
    'URFA': 'Şanlıurfa',
    'MALATYA': 'Malatya',
    'ERZURUM': 'Erzurum',
    'VAN': 'Van',
    'BATMAN': 'Batman',
    'ELAZIĞ': 'Elazığ',
    'İZMİT': 'Kocaeli',
    'DENİZLİ': 'Denizli',
    'SAMSUN': 'Samsun',
    'KAHRA': 'Kahramanmaraş',
    'SİVAS': 'Sivas',
    'BALIKESİR': 'Balıkesir',
    'TEKİRDAĞ': 'Tekirdağ',
    'ZONGULDAK': 'Zonguldak',
    'MUĞLA': 'Muğla',
    'AYDIN': 'Aydın',
    'MANİSA': 'Manisa',
    'SAKARYA': 'Sakarya',
    'ÇORUM': 'Çorum',
    'TOKAT': 'Tokat',
    'ORDU': 'Ordu',
    'TRABZON': 'Trabzon',
    'GİRESUN': 'Giresun',
    'RİZE': 'Rize',
    'ARTVİN': 'Artvin',
    'ARDAHAN': 'Ardahan',
    'KARS': 'Kars',
    'AĞRI': 'Ağrı',
    'IĞDIR': 'Iğdır',
    'TUNCELİ': 'Tunceli',
    'BİNGÖL': 'Bingöl',
    'MUŞ': 'Muş',
    'BİTLİS': 'Bitlis',
    'SİİRT': 'Siirt',
    'ŞIRNAK': 'Şırnak',
    'HAKKARİ': 'Hakkari',
    'MARDİN': 'Mardin',
    'ADIYAMAN': 'Adıyaman',
    'KİLİS': 'Kilis',
    'OSMANİYE': 'Osmaniye',
    'HATAY': 'Hatay',
    'KAHRAMANMARAŞ': 'Kahramanmaraş',
    'AMASYA': 'Amasya',
    'ÇANKIRI': 'Çankırı',
    'KIRIKKALE': 'Kırıkkale',
    'KIRŞEHİR': 'Kırşehir',
    'NEVŞEHİR': 'Nevşehir',
    'AKSARAY': 'Aksaray',
    'YOZGAT': 'Yozgat',
    'ERZİNCAN': 'Erzincan',
    'BAYBURT': 'Bayburt',
    'GÜMÜŞHANE': 'Gümüşhane'
  };

  for (const [cityKey, cityName] of Object.entries(cityMap)) {
    if (name.includes(cityKey)) {
      return cityName;
    }
  }
  
  return 'Bilinmiyor';
}

const getScoreColor = (score: number) => {
  if (score >= 85) return "text-green-600 bg-green-50";
  if (score >= 75) return "text-blue-600 bg-blue-50";
  if (score >= 65) return "text-yellow-600 bg-yellow-50";
  return "text-red-600 bg-red-50";
};

const getScoreBadgeVariant = (score: number): "default" | "secondary" | "destructive" | "outline" => {
  if (score >= 85) return "default";
  if (score >= 75) return "secondary";
  if (score >= 65) return "outline";
  return "destructive";
};

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(2022);
  const [availableYears, setAvailableYears] = useState<number[]>([2022]);

  // Fetch available years and universities on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [years, data] = await Promise.all([
          fetchAvailableYears(),
          fetchUniversities(selectedYear)
        ]);
        setAvailableYears(years);
        setUniversities(data);
        setError(null);
      } catch (err) {
        setError('Veriler yüklenirken bir hata oluştu');
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedYear]);

  const filteredAndSortedUniversities = useMemo(() => {
    let filtered = universities.filter(
      (university) =>
        university.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        university.city.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return filtered.sort((a, b) => {
      if (sortOrder === 'desc') {
        return b.overallScore - a.overallScore;
      }
      return a.overallScore - b.overallScore;
    });
  }, [universities, searchTerm, sortOrder]);

  const toggleSortOrder = () => {
    setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-full mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-6 sm:py-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 mb-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent mb-4 leading-tight">
              Üniversite Etkinlik Skorları
            </h1>
            <div className="flex items-center justify-center gap-2 mb-4">
              <Trophy className="h-6 w-6 text-yellow-500" />
              <span className="text-lg sm:text-xl font-semibold text-gray-700">Performans Analizi</span>
              <Trophy className="h-6 w-6 text-yellow-500" />
            </div>
            <p className="text-lg sm:text-xl text-gray-600 mb-2 max-w-4xl mx-auto leading-relaxed">
              <span className="font-semibold text-blue-600">YÖKAK</span> verilerine dayalı 
              <span className="font-semibold text-purple-600 mx-2">SFA analizi</span> 
              ile üniversite performans değerlendirmesi
            </p>
            <div className="flex items-center justify-center gap-4 text-sm text-gray-500 mt-4">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                <span>Güncel Veriler</span>
              </div>
              <div className="w-px h-4 bg-gray-300"></div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                <span>Bilimsel Analiz</span>
              </div>
              <div className="w-px h-4 bg-gray-300"></div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
                <span>Karşılaştırmalı Değerlendirme</span>
              </div>
            </div>
          </div>
          
          {/* Year Selector - More compact and elegant */}
          <div className="mb-6">
            <div className="flex flex-wrap gap-1 justify-center mb-3">
              {availableYears.map((year) => (
                <Button
                  key={year}
                  onClick={() => setSelectedYear(year)}
                  variant={selectedYear === year ? "default" : "outline"}
                  size="sm"
                  className={`px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
                    selectedYear === year
                      ? "bg-blue-600 text-white shadow-lg scale-105"
                      : "border-gray-300 text-gray-600 hover:bg-blue-50 hover:border-blue-300"
                  }`}
                >
                  {year}
                </Button>
              ))}
            </div>
            <div className="text-center">
              <Badge variant="secondary" className="text-xs px-3 py-1">
                📊 {selectedYear} yılı verileri aktif
              </Badge>
            </div>
          </div>

          {/* Search and Sort Controls - Better organized */}
          <div className="flex flex-col sm:flex-row gap-3 items-center justify-center max-w-2xl mx-auto">
            <div className="relative flex-1 w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                type="text"
                placeholder="Üniversite adı veya şehir ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2.5 w-full border-gray-300 focus:border-blue-400 focus:ring-blue-400 text-sm rounded-lg"
              />
            </div>
            <Button
              onClick={toggleSortOrder}
              variant="outline"
              size="sm"
              className="flex items-center gap-2 border-gray-300 text-gray-700 hover:bg-blue-50 hover:border-blue-300 px-4 py-2.5 text-sm rounded-lg"
            >
              <ArrowUpDown className="h-4 w-4" />
              {sortOrder === 'desc' ? 'Azalan' : 'Artan'}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-full mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 sm:py-10">
        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Üniversite verileri yükleniyor...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-12">
            <div className="text-red-500 mb-4">
              <Search className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Hata</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button 
              onClick={() => window.location.reload()} 
              variant="outline"
              className="border-blue-200 text-blue-700 hover:bg-blue-50"
            >
              Tekrar Dene
            </Button>
          </div>
        )}

        {/* Results Count */}
        {!loading && !error && (
          <div className="mb-4 sm:mb-6 px-1">
            <p className="text-sm sm:text-base text-gray-600">
              <span className="font-semibold text-blue-700">{filteredAndSortedUniversities.length}</span> üniversite bulundu
            </p>
          </div>
        )}

        {/* University Grid */}
        {!loading && !error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 sm:gap-6">
            {filteredAndSortedUniversities.map((university) => (
            <Card 
              key={university.id} 
              className="hover:shadow-lg transition-all duration-300 border-blue-100 hover:border-blue-200 bg-white/80 backdrop-blur-sm w-full"
            >
              <CardHeader className="pb-3 sm:pb-4 px-4 sm:px-6 pt-4 sm:pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-base sm:text-lg font-bold text-gray-900 mb-2 leading-tight break-words">
                      {university.name}
                    </CardTitle>
                    <div className="flex items-center text-gray-600 mb-2 sm:mb-3">
                      <MapPin className="h-4 w-4 mr-1" />
                      <span className="text-xs sm:text-sm">{university.city}</span>
                    </div>
                    <div className="flex items-center text-gray-500 mb-2">
                      <Trophy className="h-3 w-3 mr-1" />
                      <span className="text-xs">Sıralama: #{university.ranking}</span>
                    </div>
                  </div>
                  <Badge 
                    variant={getScoreBadgeVariant(university.overallScore)}
                    className="ml-2 font-bold text-xs sm:text-sm flex-shrink-0"
                  >
                    {university.overallScore.toFixed(1)}
                  </Badge>
                </div>
              </CardHeader>
              
              <CardContent className="pt-0 px-4 sm:px-6 pb-4 sm:pb-6">
                <div className="space-y-3 sm:space-y-4">
                  {/* Ortalama Skor */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Trophy className="h-3 w-3 sm:h-4 sm:w-4 text-yellow-600 mr-1.5 sm:mr-2 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium text-gray-700 truncate">Ortalama Skor</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-12 sm:w-16 bg-gray-200 rounded-full h-1.5 sm:h-2">
                        <div 
                          className="bg-gradient-to-r from-yellow-400 to-yellow-600 h-1.5 sm:h-2 rounded-full transition-all duration-500"
                          style={{ width: `${university.successScore}%` }}
                        ></div>
                      </div>
                      <span className={`text-xs font-semibold px-1.5 sm:px-2 py-0.5 sm:py-1 rounded ${getScoreColor(university.successScore)}`}>
                        {university.successScore}
                      </span>
                    </div>
                  </div>

                  {/* Medyan Skor */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <BookOpen className="h-3 w-3 sm:h-4 sm:w-4 text-blue-600 mr-1.5 sm:mr-2 flex-shrink-0" />
                      <span className="text-xs sm:text-sm font-medium text-gray-700 truncate">Medyan Skor</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-12 sm:w-16 bg-gray-200 rounded-full h-1.5 sm:h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-400 to-blue-600 h-1.5 sm:h-2 rounded-full transition-all duration-500"
                          style={{ width: `${university.publicationScore}%` }}
                        ></div>
                      </div>
                      <span className={`text-xs font-semibold px-1.5 sm:px-2 py-0.5 sm:py-1 rounded ${getScoreColor(university.publicationScore)}`}>
                        {university.publicationScore}
                      </span>
                    </div>
                  </div>


                  {/* Sıralama */}
                  <div className="pt-2 sm:pt-3 border-t border-gray-100">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Star className="h-3 w-3 sm:h-4 sm:w-4 text-purple-600 mr-1.5 sm:mr-2 flex-shrink-0" />
                        <span className="text-xs sm:text-sm font-bold text-gray-800 truncate">Sıralama</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-purple-700 border-purple-200">
                          #{university.ranking}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && !error && filteredAndSortedUniversities.length === 0 && (
          <div className="text-center py-8 sm:py-12 px-4">
            <div className="text-gray-400 mb-4">
              <Search className="h-12 w-12 sm:h-16 sm:w-16 mx-auto" />
            </div>
            <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-2">Sonuç bulunamadı</h3>
            <p className="text-sm sm:text-base text-gray-600">
              Arama kriterlerinizi değiştirerek tekrar deneyin.
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-blue-100 mt-20">
        <div className="max-w-full mx-auto px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16 py-8 sm:py-10">
          <div className="text-center text-gray-600">
            <p className="text-xs sm:text-sm">
              © 2024 Üniversite Etkinlik Skorları. Tüm hakları saklıdır.
            </p>
            <p className="text-xs mt-1 sm:mt-2">
              Veriler YÖKAK (Yükseköğretim Kalite Kurulu) tarafından sağlanmaktadır.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;