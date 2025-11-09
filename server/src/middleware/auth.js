import jwt from "jsonwebtoken";

export function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization || "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : null;

  if (!token) {
    return res.status(401).json({ error: "Missing token" });
  }

  try {
    const secret = process.env.JWT_SECRET || "dev_secret_change_me";
    const payload = jwt.verify(token, secret);
    req.user = { id: payload.sub, email: payload.email, name: payload.name };
    next();
  } catch (error) {
    return res.status(401).json({ error: "Invalid token" });
  }
}

export function signToken(user) {
  const secret = process.env.JWT_SECRET || "dev_secret_change_me";
  const payload = { sub: user.id, email: user.email, name: user.name };
  return jwt.sign(payload, secret, { expiresIn: "7d" });
}


