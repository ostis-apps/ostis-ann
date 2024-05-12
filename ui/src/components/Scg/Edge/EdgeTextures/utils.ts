export const getUto = (x1: number, y1: number, x2: number, y2: number ) => {
    const dx = x2 - x1;
    const dy = y2 - y1;
    // Находим длину этого вектора
    const length = Math.sqrt(dx * dx + dy * dy);

    return{
        x1: String(x1 + (dx / length) * 15),
        y1: String(y1 + (dy / length) * 15),
        x2: String(x2 - (dx / length) * 25),
        y2: String(y2 - (dy / length) * 25),
    };
};
