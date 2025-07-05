// 视频编辑器主类
class VideoEditor {
    constructor() {
        this.mediaItems = [];
        this.timelineClips = [];
        this.currentTime = 0;
        this.duration = 0;
        this.isPlaying = false;
        this.selectedClip = null;
        this.pixelsPerSecond = 50; // 时间轴缩放比例
        this.tracks = [
            { id: 1, name: '视频轨道 1', type: 'video' },
            { id: 2, name: '视频轨道 2', type: 'video' },
            { id: 3, name: '音频轨道 1', type: 'audio' }
        ];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupTimeline();
        this.updateTimeDisplay();
    }
    
    setupEventListeners() {
        // 工具栏按钮事件
        $('#import-btn').on('click', () => this.importMedia());
        $('#play-btn').on('click', () => this.togglePlayback());
        $('#stop-btn').on('click', () => this.stopPlayback());
        $('#export-btn').on('click', () => this.showExportDialog());
        
        // 导出对话框事件
        $('#export-modal .close').on('click', () => this.hideExportDialog());
        $('#export-confirm').on('click', () => this.exportVideo());
        $('#export-cancel').on('click', () => this.hideExportDialog());
        
        // 键盘快捷键
        $(document).on('keydown', (e) => this.handleKeyboard(e));
        
        // 时间轴点击事件
        $('.timeline').on('click', (e) => this.handleTimelineClick(e));
    }
    
    setupDragAndDrop() {
        // 媒体库拖放区域
        const dropZone = $('.drop-zone')[0];
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            $(dropZone).addClass('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            $(dropZone).removeClass('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            $(dropZone).removeClass('dragover');
            
            const files = Array.from(e.dataTransfer.files);
            files.forEach(file => this.addMediaFile(file));
        });
        
        // 点击导入
        dropZone.addEventListener('click', () => this.importMedia());
        
        // 媒体项拖拽到时间轴
        this.setupMediaItemDragging();
    }
    
    setupMediaItemDragging() {
        $('.media-items').on('mousedown', '.media-item', (e) => {
            const mediaItem = $(e.currentTarget);
            const mediaData = mediaItem.data('media');
            
            if (!mediaData) return;
            
            const dragHelper = $('<div class="drag-helper"></div>')
                .text(mediaData.name)
                .css({
                    position: 'fixed',
                    background: '#0078d4',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    pointerEvents: 'none',
                    zIndex: 1000,
                    left: e.clientX + 10,
                    top: e.clientY - 10
                });
            
            $('body').append(dragHelper);
            
            const handleMouseMove = (e) => {
                dragHelper.css({
                    left: e.clientX + 10,
                    top: e.clientY - 10
                });
            };
            
            const handleMouseUp = (e) => {
                $(document).off('mousemove', handleMouseMove);
                $(document).off('mouseup', handleMouseUp);
                dragHelper.remove();
                
                // 检查是否拖拽到时间轴
                const timelineElement = document.elementFromPoint(e.clientX, e.clientY);
                const track = $(timelineElement).closest('.track');
                
                if (track.length > 0) {
                    const trackIndex = track.index();
                    const timelineRect = $('.timeline')[0].getBoundingClientRect();
                    const relativeX = e.clientX - timelineRect.left - 150; // 减去轨道标签宽度
                    const time = Math.max(0, relativeX / this.pixelsPerSecond);
                    
                    this.addClipToTimeline(mediaData, trackIndex, time);
                }
            };
            
            $(document).on('mousemove', handleMouseMove);
            $(document).on('mouseup', handleMouseUp);
        });
    }
    
    setupTimeline() {
        // 创建轨道
        const tracksContainer = $('.tracks');
        tracksContainer.empty();
        
        this.tracks.forEach((track, index) => {
            const trackElement = $(`
                <div class="track" data-track-id="${track.id}">
                    <div class="track-label">${track.name}</div>
                    <div class="track-content"></div>
                </div>
            `);
            tracksContainer.append(trackElement);
        });
        
        // 设置时间轴剪辑拖拽
        this.setupClipDragging();
    }
    
    setupClipDragging() {
        $('.tracks').on('mousedown', '.timeline-clip', (e) => {
            e.stopPropagation();
            const clip = $(e.currentTarget);
            const clipData = clip.data('clip');
            
            if (!clipData) return;
            
            this.selectClip(clipData);
            
            const startX = e.clientX;
            const startLeft = parseInt(clip.css('left'));
            
            const handleMouseMove = (e) => {
                const deltaX = e.clientX - startX;
                const newLeft = Math.max(0, startLeft + deltaX);
                const newTime = newLeft / this.pixelsPerSecond;
                
                clip.css('left', newLeft + 'px');
                clipData.startTime = newTime;
                
                this.updateClipProperties(clipData);
            };
            
            const handleMouseUp = () => {
                $(document).off('mousemove', handleMouseMove);
                $(document).off('mouseup', handleMouseUp);
            };
            
            $(document).on('mousemove', handleMouseMove);
            $(document).on('mouseup', handleMouseUp);
        });
    }
    
    importMedia() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = 'video/*,audio/*,image/*';
        
        input.onchange = (e) => {
            Array.from(e.target.files).forEach(file => this.addMediaFile(file));
        };
        
        input.click();
    }
    
    addMediaFile(file) {
        const mediaItem = {
            id: Date.now() + Math.random(),
            name: file.name,
            file: file,
            type: this.getFileType(file),
            duration: 0,
            url: URL.createObjectURL(file)
        };
        
        // 获取媒体时长
        if (mediaItem.type === 'video' || mediaItem.type === 'audio') {
            const element = mediaItem.type === 'video' ? 
                document.createElement('video') : 
                document.createElement('audio');
            
            element.src = mediaItem.url;
            element.onloadedmetadata = () => {
                mediaItem.duration = element.duration;
                this.updateMediaItemDisplay(mediaItem);
            };
        }
        
        this.mediaItems.push(mediaItem);
        this.addMediaItemToLibrary(mediaItem);
    }
    
    getFileType(file) {
        if (file.type.startsWith('video/')) return 'video';
        if (file.type.startsWith('audio/')) return 'audio';
        if (file.type.startsWith('image/')) return 'image';
        return 'unknown';
    }
    
    addMediaItemToLibrary(mediaItem) {
        const itemElement = $(`
            <div class="media-item" data-media-id="${mediaItem.id}">
                <div class="media-item-info">
                    <div class="media-item-name">${mediaItem.name}</div>
                    <div class="media-item-duration">${this.formatTime(mediaItem.duration)}</div>
                </div>
            </div>
        `);
        
        itemElement.data('media', mediaItem);
        $('.media-items').append(itemElement);
    }
    
    updateMediaItemDisplay(mediaItem) {
        const itemElement = $(`.media-item[data-media-id="${mediaItem.id}"]`);
        itemElement.find('.media-item-duration').text(this.formatTime(mediaItem.duration));
    }
    
    addClipToTimeline(mediaItem, trackIndex, startTime) {
        const clip = {
            id: Date.now() + Math.random(),
            mediaId: mediaItem.id,
            trackIndex: trackIndex,
            startTime: startTime,
            duration: mediaItem.duration || 5, // 默认5秒
            name: mediaItem.name,
            type: mediaItem.type
        };
        
        this.timelineClips.push(clip);
        this.addClipToTimelineDisplay(clip);
        this.updateDuration();
    }
    
    addClipToTimelineDisplay(clip) {
        const track = $(`.track:eq(${clip.trackIndex}) .track-content`);
        const width = clip.duration * this.pixelsPerSecond;
        const left = clip.startTime * this.pixelsPerSecond;
        
        const clipElement = $(`
            <div class="timeline-clip ${clip.type}" data-clip-id="${clip.id}">
                ${clip.name}
            </div>
        `).css({
            left: left + 'px',
            width: width + 'px'
        });
        
        clipElement.data('clip', clip);
        track.append(clipElement);
    }
    
    selectClip(clip) {
        $('.timeline-clip').removeClass('selected');
        $(`.timeline-clip[data-clip-id="${clip.id}"]`).addClass('selected');
        this.selectedClip = clip;
        this.updateClipProperties(clip);
    }
    
    updateClipProperties(clip) {
        $('#prop-start-time').val(clip.startTime.toFixed(2));
        $('#prop-duration').val(clip.duration.toFixed(2));
        $('#prop-opacity').val(100);
        $('#prop-volume').val(100);
    }
    
    handleTimelineClick(e) {
        const timelineRect = $('.timeline')[0].getBoundingClientRect();
        const relativeX = e.clientX - timelineRect.left - 150;
        const time = Math.max(0, relativeX / this.pixelsPerSecond);
        
        this.setCurrentTime(time);
    }
    
    setCurrentTime(time) {
        this.currentTime = Math.max(0, Math.min(time, this.duration));
        this.updatePlayhead();
        this.updateTimeDisplay();
    }
    
    updatePlayhead() {
        const left = 150 + (this.currentTime * this.pixelsPerSecond);
        $('.playhead').css('left', left + 'px');
    }
    
    updateTimeDisplay() {
        $('.time-display').text(`${this.formatTime(this.currentTime)} / ${this.formatTime(this.duration)}`);
    }
    
    updateDuration() {
        let maxTime = 0;
        this.timelineClips.forEach(clip => {
            const endTime = clip.startTime + clip.duration;
            if (endTime > maxTime) maxTime = endTime;
        });
        this.duration = maxTime;
        this.updateTimeDisplay();
    }
    
    togglePlayback() {
        if (this.isPlaying) {
            this.pausePlayback();
        } else {
            this.startPlayback();
        }
    }
    
    startPlayback() {
        this.isPlaying = true;
        $('#play-btn i').removeClass('fa-play').addClass('fa-pause');
        
        this.playbackInterval = setInterval(() => {
            this.currentTime += 0.1;
            if (this.currentTime >= this.duration) {
                this.stopPlayback();
                return;
            }
            this.updatePlayhead();
            this.updateTimeDisplay();
        }, 100);
    }
    
    pausePlayback() {
        this.isPlaying = false;
        $('#play-btn i').removeClass('fa-pause').addClass('fa-play');
        if (this.playbackInterval) {
            clearInterval(this.playbackInterval);
        }
    }
    
    stopPlayback() {
        this.pausePlayback();
        this.setCurrentTime(0);
    }
    
    showExportDialog() {
        $('#export-modal').show();
    }
    
    hideExportDialog() {
        $('#export-modal').hide();
    }
    
    exportVideo() {
        const format = $('#export-format').val();
        const quality = $('#export-quality').val();
        
        // 这里应该调用后端API进行视频导出
        alert(`导出视频\n格式: ${format}\n质量: ${quality}\n\n注意：实际导出功能需要后端支持`);
        
        this.hideExportDialog();
    }
    
    handleKeyboard(e) {
        switch(e.key) {
            case ' ':
                e.preventDefault();
                this.togglePlayback();
                break;
            case 'Delete':
                if (this.selectedClip) {
                    this.deleteClip(this.selectedClip);
                }
                break;
            case 'ArrowLeft':
                this.setCurrentTime(this.currentTime - 1);
                break;
            case 'ArrowRight':
                this.setCurrentTime(this.currentTime + 1);
                break;
        }
    }
    
    deleteClip(clip) {
        const index = this.timelineClips.indexOf(clip);
        if (index > -1) {
            this.timelineClips.splice(index, 1);
            $(`.timeline-clip[data-clip-id="${clip.id}"]`).remove();
            this.selectedClip = null;
            this.updateDuration();
        }
    }
    
    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '00:00';
        
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// 初始化编辑器
$(document).ready(() => {
    window.videoEditor = new VideoEditor();
    
    // 添加一些示例数据用于演示
    setTimeout(() => {
        // 模拟添加示例剪辑
        const exampleClip = {
            id: 'example-1',
            name: '示例视频.mp4',
            type: 'video',
            duration: 10
        };
        
        window.videoEditor.addClipToTimeline(exampleClip, 0, 2);
    }, 500);
});