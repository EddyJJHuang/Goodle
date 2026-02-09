import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Upload, Wand2, Check, Loader2, CheckCircle } from 'lucide-react';
import client from '../api/client';

type PostMode = 'adoption' | 'lost';

const PostPet = () => {
  const navigate = useNavigate();
  const [postMode, setPostMode] = useState<PostMode>('adoption');
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [uploadedPreview, setUploadedPreview] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [submitRedirectTo, setSubmitRedirectTo] = useState<string>('/adoption');
  const [formData, setFormData] = useState({
      name: '',
      breed: '',
      color: '',
      age: '',
      personality: '',
      tags: [] as string[],
  });
  const [lostFormData, setLostFormData] = useState({
      breed: '',
      description: '',
      lost_time: '',
      address: '',
      lat: '',
      lng: '',
      contact: '',
  });

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !file.type.startsWith('image/')) return;
    setAnalyzeError(null);
    let previewUrl: string | null = null;
    try {
      previewUrl = URL.createObjectURL(file);
    } catch {
      setAnalyzeError('Could not preview this image.');
      return;
    }
    setUploadedPreview((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return previewUrl as string;
    });
    setUploadedFile(file);
    if (postMode === 'lost') {
      setAnalyzed(false);
      return;
    }
    setAnalyzing(true);
    setAnalyzed(false);
    try {
      const form = new FormData();
      form.append('photo', file);
      const res = await client.post('/analyze-pet-photo', form, { timeout: 30000 });
      const raw = res && typeof res === 'object' ? res : {};
      const data = (raw as { data?: unknown }).data;
      const payload = data && typeof data === 'object' ? (data as Record<string, unknown>) : {};
      setFormData({
        breed: typeof payload.breed === 'string' ? payload.breed : 'Unknown',
        color: typeof payload.color === 'string' ? payload.color : 'Unknown',
        tags: Array.isArray(payload.tags) ? payload.tags.filter((t): t is string => typeof t === 'string') : [],
      });
      setAnalyzed(true);
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'message' in err ? String((err as { message: unknown }).message) : '';
      const res = err && typeof err === 'object' && 'response' in err ? (err as { response?: { data?: { detail?: unknown } } }).response : undefined;
      const rawDetail = res?.data?.detail;
      let detail = '';
      if (rawDetail != null) {
        if (typeof rawDetail === 'string') detail = rawDetail;
        else if (Array.isArray(rawDetail) && rawDetail.length > 0) {
          const first = rawDetail[0];
          detail = typeof first === 'object' && first != null && 'msg' in first ? String((first as { msg: unknown }).msg) : JSON.stringify(rawDetail);
        } else if (typeof rawDetail === 'object') detail = JSON.stringify(rawDetail);
        else detail = String(rawDetail);
      }
      if (!res && (msg === 'Network Error' || msg.includes('Network Error'))) {
        setAnalyzeError('Cannot reach backend. Start it with: cd backend && source .venv/bin/activate && python run.py');
      } else if (res?.status === 429 || (typeof detail === 'string' && (detail.includes('429') || detail.includes('quota') || detail.includes('Quota exceeded')))) {
        setAnalyzeError('Daily free quota exceeded. Try again later (see https://ai.google.dev/gemini-api/docs/rate-limits). You can fill breed and color manually below and submit.');
      } else {
        setAnalyzeError(detail || msg || 'AI analysis failed. Check backend and GEMINI_API_KEY.');
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    if (postMode === 'lost') {
      const breed = (lostFormData?.breed ?? '').trim() || 'Unknown';
      const description = (lostFormData?.description ?? '').trim();
      const lost_time = (lostFormData?.lost_time ?? '').trim();
      const address = (lostFormData?.address ?? '').trim();
      const contact = (lostFormData?.contact ?? '').trim();
      const lat = (lostFormData?.lat ?? '').trim();
      const lng = (lostFormData?.lng ?? '').trim();
      try {
        const form = new FormData();
        form.append('breed', breed);
        form.append('description', description);
        form.append('lost_time', lost_time || new Date().toISOString().slice(0, 16));
        form.append('address', address);
        form.append('contact', contact);
        form.append('lat', lat);
        form.append('lng', lng);
        if (uploadedFile) form.append('photo', uploadedFile);
        await client.post('/lost-dog', form);
        setSubmitted(true);
        setSubmitRedirectTo('/lost-found');
        setTimeout(() => navigate('/lost-found'), 2000);
      } catch (err: unknown) {
        const res = err && typeof err === 'object' && 'response' in err ? (err as { response?: { data?: { detail?: unknown } } }).response : undefined;
        const raw = res?.data?.detail;
        const msg = typeof raw === 'string' ? raw : Array.isArray(raw) && raw[0] && typeof raw[0] === 'object' && 'msg' in raw[0] ? String((raw[0] as { msg: unknown }).msg) : 'Publish failed. Please try again later.';
        setSubmitError(msg);
      }
      return;
    }
    const name = (formData?.name ?? '').trim() || 'Unnamed';
    const breed = (formData?.breed ?? '').trim() || 'Unknown';
    const age = (formData?.age ?? '').trim();
    const personality = (formData?.personality ?? '').trim();
    const tags = Array.isArray(formData?.tags) ? formData.tags : [];
    try {
      const form = new FormData();
      form.append('name', name);
      form.append('breed', breed);
      form.append('age', age);
      form.append('description', personality);
      form.append('tags', tags.join(', '));
      if (uploadedFile) form.append('photo', uploadedFile);
      await client.post('/pets', form);
      setSubmitted(true);
      setSubmitRedirectTo('/adoption');
      setTimeout(() => navigate('/adoption'), 2000);
    } catch (err: unknown) {
      const res = err && typeof err === 'object' && 'response' in err ? (err as { response?: { data?: { detail?: unknown } } }).response : undefined;
      const raw = res?.data?.detail;
      const msg = typeof raw === 'string' ? raw : Array.isArray(raw) && raw[0] && typeof raw[0] === 'object' && 'msg' in raw[0] ? String((raw[0] as { msg: unknown }).msg) : 'Publish failed. Please try again later.';
      setSubmitError(msg);
    }
  };

  const handleCancel = () => {
    navigate(-1);
  };

  if (submitted) {
    return (
      <div className="flex-grow py-20 px-4 flex flex-col items-center justify-center bg-gray-50">
        <div className="bg-green-50 border border-green-200 rounded-xl p-8 max-w-md text-center">
          <CheckCircle className="mx-auto text-green-600 mb-4" size={48} />
          <h2 className="text-xl font-bold text-green-800 mb-2">Published</h2>
          <p className="text-green-700 text-sm">{submitRedirectTo === '/lost-found' ? 'Redirecting to Lost & Found…' : 'Redirecting to Adoption…'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-grow py-10 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8 text-center sm:text-left">
          <div className="flex gap-2 mb-4">
            <button type="button" onClick={() => setPostMode('adoption')} className={`px-4 py-2 rounded-lg text-sm font-medium ${postMode === 'adoption' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>Adoption Post</button>
            <button type="button" onClick={() => setPostMode('lost')} className={`px-4 py-2 rounded-lg text-sm font-medium ${postMode === 'lost' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>Lost Dog Post</button>
          </div>
          <h1 className="text-3xl font-display font-bold text-gray-900">{postMode === 'lost' ? 'Post Lost Dog' : 'Post a Pet for Adoption'}</h1>
          <p className="mt-2 text-sm text-gray-500">{postMode === 'lost' ? 'Fill in the lost dog details and contact info so others can reach you.' : 'Help a furry friend find their forever home. Please fill out the details below as accurately as possible.'}</p>
        </div>

        <form className="space-y-8" onSubmit={handleSubmit}>
          {/* Photos */}
          <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
            <div className="md:flex md:items-start md:gap-6">
              <div className="md:w-1/3 mb-4 md:mb-0">
                <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                  <Camera className="text-secondary" size={20} /> {postMode === 'lost' ? 'Dog Photo' : 'Photos'}
                </h2>
                <p className="mt-1 text-sm text-gray-500">{postMode === 'lost' ? 'Upload a photo of the lost dog for identification.' : 'Upload up to 5 photos. High quality photos increase adoption chances!'}</p>
              </div>
              <div className="md:w-2/3">
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                   <div className="col-span-2 sm:col-span-3 relative group">
                        <label className="relative flex flex-col justify-center items-center w-full h-48 rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-primary transition-all cursor-pointer">
                            <div className="space-y-1 text-center">
                                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                                <div className="text-sm text-gray-600">
                                    <span className="font-medium text-primary hover:text-orange-600">Click to upload</span> or drag and drop
                                </div>
                                <p className="text-xs text-gray-500">PNG, JPG, GIF up to 5MB</p>
                            </div>
                            <input type="file" className="sr-only" accept="image/*" onChange={handleFileSelect} />
                        </label>
                   </div>
                   {uploadedPreview && (
                       <div className="relative aspect-square rounded-lg overflow-hidden border border-gray-200">
                           <img src={uploadedPreview} alt="Uploaded" className="w-full h-full object-cover" />
                           <div className="absolute top-1 right-1 bg-green-500 rounded-full p-0.5"><Check size={12} className="text-white"/></div>
                       </div>
                   )}
                </div>
              </div>
            </div>
          </div>

          {/* AI Analysis Result (adoption only) */}
          {postMode === 'adoption' && analyzing && (
              <div className="bg-blue-50 border border-blue-100 rounded-xl p-6 flex items-center justify-center gap-3 text-blue-700 animate-pulse">
                  <Loader2 className="animate-spin" /> Analyzing photo features with Gemini AI...
              </div>
          )}

          {analyzeError && (
              <div className="bg-red-50 border border-red-100 rounded-xl p-6 text-sm text-red-700">{analyzeError}</div>
          )}
          {submitError && (
              <div className="bg-red-50 border border-red-100 rounded-xl p-6 text-sm text-red-700">{submitError}</div>
          )}
          {postMode === 'adoption' && analyzed && !analyzeError && (
              <div className="bg-green-50 border border-green-100 rounded-xl p-6">
                  <h3 className="text-green-800 font-bold flex items-center gap-2 mb-2">
                      <Wand2 size={18} /> AI Analysis Complete
                  </h3>
                  <div className="flex gap-4 text-sm text-green-700">
                      <div>
                          <span className="font-semibold">Detected Breed:</span> {formData?.breed ?? 'Unknown'}
                      </div>
                      <div>
                          <span className="font-semibold">Color:</span> {formData?.color ?? 'Unknown'}
                      </div>
                  </div>
                  <p className="text-xs text-green-600 mt-2">Breed and color are auto-filled below; you can edit them.</p>
              </div>
          )}

          {/* Details: Lost dog */}
          {postMode === 'lost' && (
          <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
              <h2 className="text-lg font-medium text-gray-900 mb-6">Lost Dog Info</h2>
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Breed</label>
                      <div className="mt-1">
                          <input type="text" value={lostFormData?.breed ?? ''} onChange={(e) => setLostFormData((f) => ({ ...(f || {}), breed: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. Golden Retriever, Poodle" />
                      </div>
                  </div>
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      <div className="mt-1">
                          <textarea rows={3} value={lostFormData?.description ?? ''} onChange={(e) => setLostFormData((f) => ({ ...(f || {}), description: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md p-3 border" placeholder="Size, color, special marks, etc." />
                      </div>
                  </div>
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Time Lost</label>
                      <div className="mt-1">
                          <input type="datetime-local" value={lostFormData?.lost_time ?? ''} onChange={(e) => setLostFormData((f) => ({ ...(f || {}), lost_time: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" />
                      </div>
                  </div>
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Location (address)</label>
                      <div className="mt-1">
                          <input type="text" value={lostFormData?.address ?? ''} onChange={(e) => setLostFormData((f) => ({ ...(f || {}), address: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="Street, area or landmark" />
                      </div>
                  </div>
                  <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Latitude (optional)</label>
                      <div className="mt-1">
                          <input type="text" value={lostFormData?.lat ?? ''} onChange={(e) => setLostFormData((f) => ({ ...(f || {}), lat: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. 31.23" />
                      </div>
                  </div>
                  <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Longitude (optional)</label>
                      <div className="mt-1">
                          <input type="text" value={lostFormData?.lng ?? ''} onChange={(e) => setLostFormData((f) => ({ ...(f || {}), lng: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. 121.47" />
                      </div>
                  </div>
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Contact</label>
                      <div className="mt-1">
                          <input type="text" value={lostFormData?.contact ?? ''} onChange={(e) => setLostFormData((f) => ({ ...(f || {}), contact: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="Phone or WeChat" required />
                      </div>
                  </div>
              </div>
          </div>
          )}

          {/* Details: Adoption */}
          {postMode === 'adoption' && (
          <div className="bg-white shadow-sm rounded-xl p-6 sm:p-8 border border-gray-100">
              <h2 className="text-lg font-medium text-gray-900 mb-6">Pet Details</h2>
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Pet Name</label>
                      <div className="mt-1">
                          <input type="text" value={formData?.name ?? ''} onChange={(e) => setFormData((f) => ({ ...(f || {}), name: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. Buddy" />
                      </div>
                  </div>
                  <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Breed</label>
                      <div className="mt-1">
                          <input type="text" value={formData?.breed ?? ''} onChange={(e) => setFormData((f) => ({ ...(f || {}), breed: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. Golden Retriever" />
                      </div>
                  </div>
                   <div className="sm:col-span-3">
                      <label className="block text-sm font-medium text-gray-700">Age</label>
                      <div className="mt-1">
                          <input type="text" value={formData?.age ?? ''} onChange={(e) => setFormData((f) => ({ ...(f || {}), age: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md py-3 px-3 border" placeholder="e.g. 2 years" />
                      </div>
                  </div>
                  <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">Personality</label>
                      <div className="mt-1">
                          <textarea rows={3} value={formData?.personality ?? ''} onChange={(e) => setFormData((f) => ({ ...(f || {}), personality: e.target.value }))} className="shadow-sm focus:ring-primary focus:border-primary block w-full sm:text-sm border-gray-300 rounded-md p-3 border" placeholder="Describe the pet's character..."></textarea>
                      </div>
                  </div>
              </div>
          </div>
          )}

          <div className="flex justify-end gap-3 pt-4">
               <button type="button" onClick={handleCancel} className="bg-white py-3 px-6 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">Cancel</button>
               <button type="submit" className="bg-primary border border-transparent rounded-md shadow-sm py-3 px-8 text-sm font-bold text-white hover:bg-orange-500 transform hover:-translate-y-0.5 transition-all">{postMode === 'lost' ? 'Post Lost Dog' : 'Post Adoption Request'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PostPet;