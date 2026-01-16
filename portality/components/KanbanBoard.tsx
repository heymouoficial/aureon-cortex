import React, { useMemo } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragOverEvent,
  DragEndEvent,
  defaultDropAnimationSideEffects,
  DropAnimation,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Task } from '../types';
import { getCurrentBrand } from '../config/branding';
import { CheckSquare, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';

interface KanbanBoardProps {
  tasks: Task[];
  onUpdateTaskStatus: (id: string, newStatus: Task['status']) => void;
}

const COLUMNS: { id: Task['status']; title: string; icon: React.ReactNode }[] = [
    { id: 'todo', title: 'Por Hacer', icon: <AlertCircle size={16} /> },
    { id: 'in-progress', title: 'En Progreso', icon: <Clock size={16} /> },
    { id: 'review', title: 'Revisión', icon: <CheckSquare size={16} /> },
    { id: 'done', title: 'Completado', icon: <CheckCircle2 size={16} /> },
];

export const KanbanBoard: React.FC<KanbanBoardProps> = ({ tasks, onUpdateTaskStatus }) => {
  const brand = getCurrentBrand();
  const [activeId, setActiveId] = React.useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
        activationConstraint: {
            distance: 5, // Prevent accidental drags
        },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Group tasks by status
  const tasksByStatus = useMemo(() => {
    const grouped: Record<string, Task[]> = {
        'todo': [],
        'in-progress': [],
        'review': [],
        'done': []
    };
    tasks.forEach(task => {
        if (grouped[task.status]) {
            grouped[task.status].push(task);
        } else {
            // Fallback for unknown statuses
            grouped['todo'].push(task);
        }
    });
    return grouped;
  }, [tasks]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragOver = (event: DragOverEvent) => {
    // Optional: Visual feedback during drag over columns
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    
    if (!over) {
        setActiveId(null);
        return;
    }

    const activeTask = tasks.find(t => t.id === active.id);
    const overContainerId = over.id as string; // Could be a task ID or column ID

    if (!activeTask) {
        setActiveId(null);
        return;
    }

    // Determine target status
    let newStatus: Task['status'] | undefined;

    // Check if dropped explicitly on a column container
    if (COLUMNS.find(c => c.id === overContainerId)) {
        newStatus = overContainerId as Task['status'];
    } 
    // Check if dropped on another task
    else {
        const overTask = tasks.find(t => t.id === overContainerId);
        if (overTask) {
            newStatus = overTask.status;
        }
    }

    if (newStatus && newStatus !== activeTask.status) {
        onUpdateTaskStatus(activeTask.id, newStatus);
    }
    
    setActiveId(null);
  };

  const dropAnimation: DropAnimation = {
    sideEffects: defaultDropAnimationSideEffects({
      styles: {
        active: {
          opacity: '0.5',
        },
      },
    }),
  };

  const activeTask = tasks.find(t => t.id === activeId);

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4 h-[calc(100vh-250px)] min-h-[500px]">
        {COLUMNS.map((col) => (
          <KanbanColumn
            key={col.id}
            id={col.id}
            title={col.title}
            icon={col.icon}
            tasks={tasksByStatus[col.id]}
            color={brand.colors.primary}
          />
        ))}
      </div>

      <DragOverlay dropAnimation={dropAnimation}>
        {activeId && activeTask ? (
            <TaskCard task={activeTask} isOverlay />
        ) : null}
      </DragOverlay>
    </DndContext>
  );
};

interface KanbanColumnProps {
    id: string;
    title: string;
    icon: React.ReactNode;
    tasks: Task[];
    color: string;
}

const KanbanColumn: React.FC<KanbanColumnProps> = ({ id, title, icon, tasks, color }) => {
    const { setNodeRef } = useDroppable({ id });

    return (
        <div 
            ref={setNodeRef}
            className="flex-shrink-0 w-72 bg-white/[0.03] border border-white/10 rounded-xl flex flex-col backdrop-blur-sm"
        >
            {/* Header */}
            <div className="p-3 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-200">
                    {icon}
                    {title}
                </div>
                <span className="text-xs bg-white/10 px-2 py-0.5 rounded-full text-gray-400">
                    {tasks.length}
                </span>
            </div>

            {/* List */}
            <div className="p-2 flex-1 overflow-y-auto space-y-2">
                <SortableContext 
                    items={tasks.map(t => t.id)} 
                    strategy={verticalListSortingStrategy}
                >
                    {tasks.map(task => (
                        <SortableTaskItem key={task.id} task={task} />
                    ))}
                </SortableContext>
                {tasks.length === 0 && (
                    <div className="h-full flex items-center justify-center text-gray-600/50 text-xs italic min-h-[100px]">
                        Vacío
                    </div>
                )}
            </div>
        </div>
    );
};

// Wrapper for Sortable item
const SortableTaskItem = ({ task }: { task: Task }) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging
    } = useSortable({ id: task.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.3 : 1,
    };

    return (
        <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
            <TaskCard task={task} />
        </div>
    );
};

import { useDroppable } from '@dnd-kit/core';

// Actual Card UI
const TaskCard = ({ task, isOverlay = false }: { task: Task, isOverlay?: boolean }) => {
    const priorityColor = task.priority === 'high' ? 'bg-red-500/20 text-red-300 border-red-500/30' : 
                          task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' : 
                          'bg-blue-500/20 text-blue-300 border-blue-500/30';

    return (
        <div className={`
            p-3 rounded-lg border border-white/5 bg-white/[0.05] hover:bg-white/[0.08] transition-all cursor-grab active:cursor-grabbing group
            ${isOverlay ? 'shadow-2xl ring-2 ring-indigo-500/50 rotate-2' : ''}
        `}>
            <div className="flex justify-between items-start mb-2">
                <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded border ${priorityColor}`}>
                    {task.priority === 'high' ? 'Alta' : task.priority === 'medium' ? 'Media' : 'Baja'}
                </span>
                {task.assignedTo && (
                    <div className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center text-[9px] font-bold text-gray-300">
                        {task.assignedTo}
                    </div>
                )}
            </div>
            
            <p className="text-sm font-medium text-gray-100 line-clamp-2 leading-snug">
                {task.title}
            </p>

            <div className="mt-2 flex items-center justify-between text-[10px] text-gray-500">
                <div className="flex gap-1">
                    {task.tags?.slice(0, 2).map(tag => (
                        <span key={tag} className="px-1 rounded bg-white/5">{tag}</span>
                    ))}
                </div>
                {task.dueDate && (
                    <span>{new Date(task.dueDate).toLocaleDateString()}</span>
                )}
            </div>
        </div>
    );
};

export default KanbanBoard;
